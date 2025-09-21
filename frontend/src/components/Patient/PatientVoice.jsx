import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { startVoiceAgent } from "../../api/voiceAgent"; // 👈 new API helper

export default function PatientVoice() {
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    // Start the voice agent as soon as we enter this page
    const activateAgent = async () => {
      try {
        setIsActive(true);
        await startVoiceAgent();
        console.log("Voice agent started");
      } catch (err) {
        console.error("Failed to start voice agent:", err);
        setIsActive(false);
      }
    };

    activateAgent();
  }, []);

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-white">
      {/* Animated Circle */}
      <div
        className={`w-48 h-48 rounded-full flex items-center justify-center mb-6 transition ${
          isActive ? "bg-green-400 animate-pulse" : "bg-gray-200"
        }`}
      >
        <span className="text-white text-3xl">{isActive ? "🎤" : "👤"}</span>
      </div>

      <p className="mb-4 text-lg">
        {isActive ? "Speaking with AI agent..." : "Agent inactive"}
      </p>

      {/* End Conversation */}
      <Link
        to="/patient/report"
        className="bg-red-500 text-white px-6 py-3 rounded-lg"
        onClick={() => setIsActive(false)} // stop pulsing when leaving
      >
        End Conversation
      </Link>
    </div>
  );
}
