#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import copy
import argparse
import itertools
import json
from collections import Counter, deque

import cv2 as cv
import numpy as np
import mediapipe as mp
import asyncio
import websockets
from flask import Flask, Response
from flask_cors import CORS

# Import your helper modules and models
from utils import CvFpsCalc
from model import KeyPointClassifier
from model import PointHistoryClassifier

# --- Flask setup ---
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your frontend

WEBSOCKET_PORT = 8765

# --- Initialize your modules exactly as in your existing code ---
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)
    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)
    # Pass an empty list so argparse does not try to interpret command-line args in a server context.
    args = parser.parse_args([])
    return args

# Get arguments (you can hardcode these values if preferred)
args = get_args()
cap_device = args.device
cap_width = args.width
cap_height = args.height
use_static_image_mode = args.use_static_image_mode
min_detection_confidence = args.min_detection_confidence
min_tracking_confidence = args.min_tracking_confidence
use_brect = True

# Camera preparation
cap = cv.VideoCapture(cap_device)
cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

# Model load
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=2,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
)
keypoint_classifier = KeyPointClassifier()
point_history_classifier = PointHistoryClassifier()

# Read labels
with open('model/keypoint_classifier/keypoint_classifier_label.csv',
          encoding='utf-8-sig') as f:
    keypoint_classifier_labels = [row[0] for row in csv.reader(f)]
with open('model/point_history_classifier/point_history_classifier_label.csv',
          encoding='utf-8-sig') as f:
    point_history_classifier_labels = [row[0] for row in csv.reader(f)]

# FPS measurement and coordinate histories
cvFpsCalc = CvFpsCalc(buffer_len=10)
history_length = 16
point_history = deque(maxlen=history_length)
finger_gesture_history = deque(maxlen=history_length)
global_zoom_factor = 1.0
mode = 0

# --- Helper Functions ---
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.empty((0, 2), int)
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point = [np.array((landmark_x, landmark_y))]
        landmark_array = np.append(landmark_array, landmark_point, axis=0)
    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_point = []
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point.append([landmark_x, landmark_y])
    return landmark_point

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]
        temp_landmark_list[index][0] -= base_x
        temp_landmark_list[index][1] -= base_y
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(list(map(abs, temp_landmark_list)))
    temp_landmark_list = list(map(lambda n: n / max_value, temp_landmark_list))
    return temp_landmark_list

def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]
    temp_point_history = copy.deepcopy(point_history)
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]
        temp_point_history[index][0] = (temp_point_history[index][0] - base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] - base_y) / image_height
    temp_point_history = list(itertools.chain.from_iterable(temp_point_history))
    return temp_point_history

def logging_csv(number, mode, landmark_list, point_history_list):
    if mode == 0:
        pass
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    if mode == 2 and (0 <= number <= 9):
        csv_path = 'model/point_history_classifier/point_history.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *point_history_list])
    return

def draw_landmarks(image, landmark_point):
    if len(landmark_point) > 0:
        # Thumb
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]), (255, 255, 255), 2)
        # Index finger
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]), (255, 255, 255), 2)
        # Middle finger
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]), (255, 255, 255), 2)
        # Ring finger
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]), (255, 255, 255), 2)
        # Little finger
        cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]), (255, 255, 255), 2)
        # Palm
        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]), (255, 255, 255), 2)
    return image

def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]), (0, 0, 0), 1)
    return image

def draw_info_text(image, brect, handedness, hand_sign_text, finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22), (0, 0, 0), -1)
    info_text = handedness.classification[0].label
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    if finger_gesture_text != "":
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)
    return image

def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, (point[0], point[1]), 1 + int(index / 2), (152, 251, 152), 2)
    return image

def draw_info(image, fps, mode, number):
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
    cv.putText(image, "FPS:" + str(fps), (10, 30),cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)
    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    return image

# --- Generator function: stream frames instead of using cv.imshow ---
def gen_frames():
    global mode, global_zoom_factor
    while True:
        fps = cvFpsCalc.get()

        # Capture frame from the camera
        ret, image = cap.read()
        if not ret:
            break

        # Mirror the frame
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)

        # Mediapipe processing
        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = hands.process(image_rgb)
        image_rgb.flags.writeable = True

        zoom_computed = False  # Not used in streaming mode

        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                pre_processed_landmark_list = pre_process_landmark(landmark_list)
                pre_processed_point_history_list = pre_process_point_history(debug_image, point_history)
                logging_csv(-1, mode, pre_processed_landmark_list, pre_processed_point_history_list)
                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                if hand_sign_id == 2:  # "Point gesture"
                    point_history.append(landmark_list[8])
                else:
                    point_history.append([0, 0])
                finger_gesture_id = 0
                if len(pre_processed_point_history_list) == (history_length * 2):
                    finger_gesture_id = point_history_classifier(pre_processed_point_history_list)
                finger_gesture_history.append(finger_gesture_id)
                most_common_fg_id = Counter(finger_gesture_history).most_common()

                if handedness.classification[0].label == "Right":
                    thumb = landmark_list[4]
                    index_finger = landmark_list[8]
                    distance = np.hypot(index_finger[0] - thumb[0], index_finger[1] - thumb[1])
                    min_distance = 30
                    max_distance = 250
                    global_zoom_factor = np.interp(distance, [min_distance, max_distance], [1.0, 3.0])
                    cv.putText(debug_image, f"Zoom: {global_zoom_factor:.2f}", (10, 130), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2, cv.LINE_AA)
                else:
                    global_zoom_factor = 1.0

                # Left hand rotate hand gesture 
                # if handedness.classification[0].label == "Left":
                #    index_finger = landmark_list[8]
                    

                debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(debug_image, brect, handedness,keypoint_classifier_labels[hand_sign_id], point_history_classifier_labels[most_common_fg_id[0][0]])
        else:
            point_history.append([0, 0])

        debug_image = draw_point_history(debug_image, point_history)
        debug_image = draw_info(debug_image, fps, mode, -1)

        # Encode the processed debug_image as JPEG
        ret, buffer = cv.imencode('.jpg', debug_image)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()

        # Yield the frame in a multipart format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
# --- Flask route to serve the video stream ---
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Asynchronous WebSocket server to send gesture data ---
# This example uses the websockets library.
async def gesture_server(websocket, path):
    # In a production system, you’d share gesture data between the video stream and WebSocket.
    # Here, as an example, we wait for a gesture event and send the current zoom factor.
    while True:
        await asyncio.sleep(0.1)
        # For example, send the zoom factor every 100ms.
        gesture_data = {"gesture": "zoom", "value": float(global_zoom_factor)}
        await websocket.send(json.dumps(gesture_data))

# Function to run the WebSocket server in the background
def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(gesture_server, "0.0.0.0", WEBSOCKET_PORT)
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == '__main__':
    # Run the WebSocket server on a background thread:
    import threading
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()

    # Run the Flask app (for video streaming)
    app.run(host='0.0.0.0', port=5025, debug=True)
