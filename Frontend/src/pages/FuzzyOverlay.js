// FuzzyOverlay.js
import React from "react";
import "./FuzzyOverlay.css";

function FuzzyOverlay() {
  // Use an absolute URL to reference the noise.png in the public folder.
  const overlayStyle = {
    backgroundImage: 'url("/noise.png")'
  };

  return <div className="fuzzy-overlay" style={overlayStyle}></div>;
}

export default FuzzyOverlay;
