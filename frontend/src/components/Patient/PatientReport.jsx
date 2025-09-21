import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchLatestNote } from "../../api/latestNote";

export default function PatientReport() {
  const [note, setNote] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLatestNote()
      .then(setNote)
      .catch((err) => {
        console.error("Failed to load latest note", err);
      });
  }, []);

  if (!note) return <p>Loading latest note...</p>;

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-50 p-6">
      <h2 className="text-xl font-bold mb-4">Report Summary</h2>
      <div className="bg-white shadow p-4 rounded-lg w-full max-w-md mb-6">
        <p>
          <strong>Name:</strong> {note.patient_name || "Unknown"}
        </p>
        <p>
          <strong>Chief Complaint:</strong> {note.chief_complaint || "N/A"}
        </p>
        <div>
          <strong>Symptoms:</strong>
          <ul className="list-disc pl-5">
            {note.symptoms?.map((s, idx) => (
              <li key={idx}>{s}</li>
            ))}
          </ul>
        </div>
      </div>
      <div className="flex gap-4">
        <button
          className="bg-green-500 text-white px-6 py-2 rounded-lg"
          onClick={() => navigate("/")}
        >
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
