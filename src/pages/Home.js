import React from "react";
import { useNavigate } from "react-router";

function Home() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate("/game");
  };

  return (
    <div className="app-wrapper">
      {/* Header section inside title */}
      <div className="title">
        <div className="header-section">
          <p>Paracosm</p>
        </div>
      </div>

      {/* Content section for the text-boxes */}
      <div className="text">
        <div className="text-box-section">
          <p>{"> PERSONAL"}</p>
        </div>
        <div className="text-box-section">
          <p>{"> SHARED"}</p>
        </div>
        <div className="text-box-section">
          <p>{"> VIRTUAL"}</p>
          <button className="styled-button" onClick={handleStart}>
            {"> START <"}
          </button>
        </div>
        <div className="text-box-section">
          <p>{"> DATA"}</p>
        </div>
      </div>
    </div>
  );
}

export default Home;