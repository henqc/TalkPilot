"use client";

import type React from "react";

import { useState, useEffect, useRef } from "react";
import { Mic, ArrowLeft } from "./assets/Icon";

interface ProductPageProps {
  onBack: () => void;
}

function ProductPage({ onBack }: ProductPageProps) {
  const [micActive, setMicActive] = useState(false);
  const [soundThreshold, setSoundThreshold] = useState(50);
  const [silenceDuration, setSilenceDuration] = useState(5);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [milliseconds, setMilliseconds] = useState(0);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (micActive) {
      const startTime = Date.now() - (timeElapsed * 1000 + milliseconds);
      timerRef.current = window.setInterval(() => {
        const elapsed = Date.now() - startTime;
        setTimeElapsed(Math.floor(elapsed / 1000));
        setMilliseconds(elapsed % 1000);
      }, 10);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [micActive]);

  const toggleMic = () => {
    if (!micActive) {
      setTimeElapsed(0);
      setMilliseconds(0);
    }
    setMicActive(!micActive);
  };

  const formatTime = (seconds: number, ms: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}:${Math.floor(ms / 10)
      .toString()
      .padStart(2, "0")}`;
  };

  return (
    <div className="product-container">
      <div className="grid-background"></div>
      <div className="product-panel">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft />
          <span>Back</span>
        </button>

        <div className="product-layout">
          <div className="left-section">
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
          </div>

          <div className="right-section">
            <div className="timer-display">
              <span>Time Elapsed</span>
              <div className="time-value">
                {formatTime(timeElapsed, milliseconds)}
              </div>
            </div>

            <div className="sliders-container">
              <div className="slider-group">
                <label htmlFor="sound-threshold">Sound Threshold</label>
                <div className="slider-with-value">
                  <div className="slider-container">
                    <input
                      type="range"
                      id="sound-threshold"
                      min="0"
                      max="100"
                      value={soundThreshold}
                      onChange={(e) =>
                        setSoundThreshold(Number.parseInt(e.target.value))
                      }
                      className="horizontal-slider"
                      style={
                        {
                          "--value": `${soundThreshold}%`,
                        } as React.CSSProperties
                      }
                    />
                  </div>
                  <span className="slider-value">{soundThreshold}%</span>
                </div>
              </div>

              <div className="slider-group">
                <label htmlFor="silence-duration">Silence Duration</label>
                <div className="slider-with-value">
                  <div className="slider-container">
                    <input
                      type="range"
                      id="silence-duration"
                      min="0"
                      max="10"
                      value={silenceDuration}
                      onChange={(e) =>
                        setSilenceDuration(Number.parseInt(e.target.value))
                      }
                      className="horizontal-slider"
                      style={
                        {
                          "--value": `${(silenceDuration / 10) * 100}%`,
                        } as React.CSSProperties
                      }
                    />
                  </div>
                  <span className="slider-value">{silenceDuration}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductPage;
