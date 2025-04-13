import React, { useState } from "react";
import "./Game.css";


function Game() {
  const [showCamera, setShowCamera] = useState(false);

  const handleBegin = () => {
    setShowCamera(true);
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
            <h2 className="Section1-text">{"> SECTION 1 - Command With Movement"}</h2>
            <p className="Section1-content">Shift your world with a gesture. Rotate. Zoom. Explore a place born from your command.</p>
            <h2 className="Section2-text">{"> SECTION 2 - Speech Manipulatiom"}</h2>
            <p className="Section2-content">Command your virtual space with your voice; let every word transform your surroundings.</p>
            <h2 className="Section3-text">{"> SECTION 3 - Explore Your Creation"}</h2>
            <p className="Section3-content">Plunge into the World You’ve Crafted</p>
          </div>
        )}
      </div>

      <div className="vertical-divider"></div>

      {/* Right section */}
      <div className="right-section">
        <div className="right-divider"></div>
        <h1 className="right-title">
          THE MAP IS BLANK. THE MEMORY IS YOURS. BUILD THE <span className="blink">UNSEEN</span>
        </h1>
        <div className="right-buttons">
          <button className="generate-random">{"> GENERATE"}<span className="blink2">_</span></button>
          <button className="vr-activation-button">{"> ENTER"}<span className="blink2">_</span></button>
        </div>
        <div className="button-border"></div>
        {/* Additional right-side content can be placed here */}
      </div>

      <button className="bottom-left-button" onClick={handleBegin}>
        {"> BEGIN"}
      </button>
    </div>
  );
}

export default Game;
