import "./App.css";

interface LandingPageProps {
  onGetStarted: () => void;
}

function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="landing-container">
      <div className="grid-background"></div>
      <div className="content">
        <h1 className="title">Talk Pilot</h1>
        <p className="subtitle">
          Empowering users to transform thoughts into actions
          <br />
          with voice commands
        </p>
      </div>
      <button className="get-started-button" onClick={onGetStarted}>
        Get Started
      </button>
    </div>
  );
}

export default LandingPage;
