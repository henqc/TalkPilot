"use client";

import { useState } from "react";
import { Mic, ArrowLeft } from "./assets/Icon";

interface ProductPageProps {
  onBack: () => void;
}

function ProductPage({ onBack }: ProductPageProps) {
  const [micActive, setMicActive] = useState(false);
  const [soundThreshold, setSoundThreshold] = useState(50);
  const [silenceDuration, setSilenceDuration] = useState(5);

  const toggleMic = () => {
    setMicActive(!micActive);
    console.log("Mic toggled:", !micActive);
  };

  return (
    <div className="product-container">
      <div className="grid-background"></div>
      <div className="product-content">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft />
          <span>Back</span>
        </button>

        <div className="mic-container">
          <button
            className={`mic-button ${micActive ? "active" : ""}`}
            onClick={toggleMic}
          >
            <Mic />
            <div className="mic-ripple"></div>
          </button>
          <p className="mic-status">
            {micActive ? "Listening..." : "Click to start"}
          </p>
        </div>

        <div className="sliders-container">
          <div className="slider-group">
            <label htmlFor="sound-threshold">Sound Threshold</label>
            <div className="slider-with-value">
              <input
                type="range"
                id="sound-threshold"
                min="0"
                max="100"
                value={soundThreshold}
                onChange={(e) => {
                  setSoundThreshold(Number.parseInt(e.target.value));
                  console.log(e.target.value);
                }}
                className="horizontal-slider"
              />
              <span className="slider-value">{soundThreshold}%</span>
            </div>
          </div>

          <div className="slider-group">
            <label htmlFor="silence-duration">Silence Duration</label>
            <div className="slider-with-value">
              <input
                type="range"
                id="silence-duration"
                min="0"
                max="10"
                value={silenceDuration}
                onChange={(e) => {
                  setSilenceDuration(Number.parseInt(e.target.value));
                  console.log(e.target.value);
                }}
                className="horizontal-slider"
              />
              <span className="slider-value">{silenceDuration}s</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductPage;
