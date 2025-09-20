import { Link } from "react-router-dom";

export default function PatientVoice() {
  return (
    <div className="h-screen flex flex-col items-center justify-center bg-white">
      <div className="w-48 h-48 rounded-full bg-gray-200 flex items-center justify-center mb-6 animate-pulse">
        <span className="text-gray-600 text-xl">👤</span>
      </div>
      <p className="mb-4 text-lg">Speaking with AI agent...</p>
      <Link
        to="/patient/report"
        className="bg-green-500 text-white px-6 py-3 rounded-lg"
      >
        End Conversation
      </Link>
    </div>
  );
}
