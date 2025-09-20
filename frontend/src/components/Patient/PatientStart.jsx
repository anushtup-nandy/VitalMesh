import { Link } from "react-router-dom";

export default function PatientStart() {
  return (
    <div className="h-screen flex flex-col items-center justify-center bg-blue-50">
      <h2 className="text-2xl font-semibold mb-6">AI Health Liaison</h2>
      <Link
        to="/patient/voice"
        className="bg-green-500 text-white px-8 py-6 rounded-full text-xl shadow-lg animate-pulse"
      >
        🎤 Speak to Liaison
      </Link>
    </div>
  );
}
