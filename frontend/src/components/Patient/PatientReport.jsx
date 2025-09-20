import { Link } from "react-router-dom";

export default function PatientReport() {
  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-50 p-6">
      <h2 className="text-xl font-bold mb-4">Report Summary</h2>
      <div className="bg-white shadow p-4 rounded-lg w-full max-w-md mb-6">
        <p>
          <strong>Pathway:</strong> Scheduling
        </p>
        <p>
          <strong>Details:</strong> Example collected details here...
        </p>
      </div>
      <div className="flex gap-4">
        <button className="bg-green-500 text-white px-6 py-2 rounded-lg">
          ✅ Confirm
        </button>
        <Link
          to="/patient/voice"
          className="bg-red-500 text-white px-6 py-2 rounded-lg"
        >
          ❌ Edit
        </Link>
      </div>
    </div>
  );
}
