import { Link } from "react-router-dom";

// This code assumes your image files are in the `public` folder.

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

      <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 w-full max-w-4xl">
        
        {/* Patient Section */}
        <div className="flex flex-col text-center items-center">
          <img src="/patient-icon.png" alt="Patient Icon" className="w-36 h-36 mb-8" />
          <Link
            to="/patient"
            className="w-full bg-green-500 text-white px-8 py-3 rounded-xl shadow-lg hover:bg-green-600 transition-colors duration-300 font-semibold text-lg"
          >
            I am a Patient
          </Link>
        </div>

        {/* Clinical Section */}
        <div className="flex flex-col text-center items-center">
          <img src="/clinician-icon.png" alt="Clinical Icon" className="w-36 h-36 mb-8" />
          <Link
            to="/clinical/login"
            className="w-full bg-blue-500 text-white px-8 py-3 rounded-xl shadow-lg hover:bg-blue-600 transition-colors duration-300 font-semibold text-lg"
          >
            I am a Clinician
          </Link>
        </div>

      </div>
    </div>
  );
}
