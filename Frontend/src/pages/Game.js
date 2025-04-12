import React, { useState } from "react";
import "./Game.css";

function Game() {
  const [showCamera, setShowCamera] = useState(false);

  const handleBegin = () => {
    setShowCamera(true);
  };

  return (
    <div className="game-container">
      {/* Fixed top border block */}
      <div className="top-left-block"></div>

      {/* Left section positioned from just below the top block to the bottom */}
      <div className="left-section">
        {showCamera ? (
          // Camera container: shows the video feed full-width of the left area
          <div className="camera-container">
            <img
              className="camera-feed"
              src="http://localhost:5025/video_feed"
              alt="Camera Feed"
            />
          </div>
        ) : (
          // Text container: shows your original text when the camera feed is not active
          <div className="text-container">
            <h2>Section 1</h2>
            <p>This is some content for section 1.</p>
          </div>
        )}
      </div>

      {/* Fixed vertical divider */}
      <div className="vertical-divider"></div>

      {/* Fixed bottom-left button spanning entire left area */}
      <button className="bottom-left-button" onClick={handleBegin}>
        {"> BEGIN"}
      </button>
    </div>
  );
}

export default Game;
