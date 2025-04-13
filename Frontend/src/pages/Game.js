import React, { useState } from "react";
import FuzzyOverlay from "./FuzzyOverlay";
import "./Game.css";

function Game() {
  const [showCamera, setShowCamera] = useState(false);

  const handleBegin = () => {
    setShowCamera(true);
  };

  const handleVR = () => {

  };

  return (
    <div className="game-container">
      {/* Render the overlay first */}

      <div className="top-left-block"></div>

      <div className="left-section">
        {showCamera ? (
          <div className="camera-container">
            <img
              className="camera-feed"
              src="http://localhost:5025/video_feed"
              alt="Camera Feed"
            />
          </div>
        ) : (
          <div className="text-container">
            <h2>{"> SECTION 1"}</h2>
            <p>Shift your world with a gesture. Rotate. Zoom. Explore a place born from silence.</p>
          </div>
        )}
      </div>

      <div className="vertical-divider"></div>

      {/* Right section */}
      <div className="right-section">
        <div className="right-divider"></div>
        <h1 className="right-title">
          THE MAP IS BLANK. THE MEMORY IS YOURS. BUILD THE UNSEEN
        </h1>
        <div className="right-buttons">
          <button className="generate-random">{"> GENERATE"}</button>
          <button className="vr-activation-button">{"> ENTER"}</button>
        </div>
        {/* Additional right-side content can be placed here */}
      </div>

      <button className="bottom-left-button" onClick={handleBegin}>
        {"> BEGIN"}
      </button>
    </div>
  );
}

export default Game;
