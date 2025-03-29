"use client";

import { useState } from "react";
import "./App.css";
import LandingPage from "./LandingPage";
import ProductPage from "./ProductPage";

function App() {
  const [currentPage, setCurrentPage] = useState("landing");

  return (
    <div className="app">
      {currentPage === "landing" ? (
        <LandingPage onGetStarted={() => setCurrentPage("product")} />
      ) : (
        <ProductPage onBack={() => setCurrentPage("landing")} />
      )}
    </div>
  );
}

export default App;
