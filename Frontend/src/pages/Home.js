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

      {/* New container for text boxes and the paragraph box */}
      <div className="content-container">
        {/* Left side: Text boxes */}
        <div className="text">
          <div className="text-box-section">
            <p>{"> PERSONAL"}</p>
          </div>
          <div className="text-box-section">
            <p>{"> VIRTUAL"}</p>
            <button className="styled-button" onClick={handleStart}>
              {"> START <"}
            </button>
          </div>
          <div className="text-box-section">
            <p>{"> SHARED"}</p>
          </div>
        </div>

        {/* Right side: Paragraph box */}
        <div className="paragraph">
          <div className="paragraph-box-section">
            <p> {"What is the shared folder for? Who knows! But it's in the screenshots and so we're using it!"} </p>
            <p> {"This is just going to be a really long-winded string literal that allows me to test such things as text wrapping, and scrolling."}</p>
            <p> {"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus posuere libero at nulla dignissim porta. Etiam quam nibh, tempor et lectus id, viverra fringilla augue. Sed sed laoreet erat. Etiam tempor eget felis eget porta. Aenean purus arcu, venenatis et cursus."} </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;