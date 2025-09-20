import { Link } from "react-router-dom";

// No image imports are needed when using the public folder.

export default function Landing() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-b from-blue-100 to-white p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-800">
          Welcome to VitalMesh
        </h1>
        <p className="text-lg text-gray-600 mt-2">
          Connecting patients and providers seamlessly.
        </p>
      </div>

      <div className="flex flex-col md:flex-row items-stretch justify-center gap-8 md:gap-12 w-full max-w-4xl">
        
        {/* Patient Card */}
        <div className="flex-1 flex flex-col bg-white p-8 rounded-2xl shadow-lg text-center items-center">
          {/* The src path is a direct string starting with "/" */}
          <img src="/patient-icon.png" alt="Patient Icon" className="w-24 h-24 mb-6" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Patient Side
          </h2>
          <div className="flex-grow"></div> {/* Pushes button to the bottom */}
          <Link
            to="/patient"
            className="w-full bg-green-500 text-white px-6 py-3 rounded-xl shadow hover:bg-green-600 transition-colors duration-300 font-semibold text-lg"
          >
            I am a Patient
          </Link>
        </div>

        {/* Clinical Card */}
        <div className="flex-1 flex flex-col bg-white p-8 rounded-2xl shadow-lg text-center items-center">
          {/* The src path is a direct string starting with "/" */}
          <img src="/clinician-icon.png" alt="Clinical Icon" className="w-24 h-24 mb-6" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Clinical Side
          </h2>
          <div className="flex-grow"></div> {/* Pushes button to the bottom */}
          <Link
            to="/clinical/login"
            className="w-full bg-blue-500 text-white px-6 py-3 rounded-xl shadow hover:bg-blue-600 transition-colors duration-300 font-semibold text-lg"
          >
            I am a Clinician
          </Link>
        </div>

      </div>
    </div>
  );
}
