import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPatient } from "../../api/patientApi";

export default function PatientDetail() {
  const { patientId } = useParams();
  const [patientData, setPatientData] = useState(null);

  useEffect(() => {
    if (patientId) {
      fetchPatient(patientId)
        .then(setPatientData)
        .catch((err) => console.error("Failed to fetch patient:", err));
    }
  }, [patientId]);

  if (!patientData) return <p>Loading...</p>;

  const {
    patient_info,
    chief_complaint,
    symptoms,
    assessment,
    recommendations,
    urgency_level,
  } = patientData;

  // Helper to safely render arrays of strings or objects
  // Recursively render objects and arrays as strings or lists
  const renderItem = (item) => {
    if (typeof item === "string" || typeof item === "number") return item;
    if (Array.isArray(item))
      return (
        <ul>
          {item.map((sub, idx) => (
            <li key={idx}>{renderItem(sub)}</li>
          ))}
        </ul>
      );
    if (typeof item === "object" && item !== null)
      return (
        <ul>
          {Object.entries(item).map(([key, value], idx) => (
            <li key={idx}>
              <strong>{key}:</strong> {renderItem(value)}
            </li>
          ))}
        </ul>
      );
    return String(item);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Patient {patientId}</h2>

      <div className="bg-white shadow p-4 rounded-lg mb-6">
        <p>
          <strong>Name:</strong> {patient_info?.name || "Unknown"}
        </p>
        <p>
          <strong>Chief Complaint:</strong> {chief_complaint || "N/A"}
        </p>
        <p>
          <strong>Urgency:</strong> {urgency_level || "N/A"}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-100 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Symptoms</h3>
          {renderItem(symptoms)}
        </div>

        <div className="bg-green-100 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Assessment</h3>
          {renderItem(assessment)}
        </div>

        <div className="bg-yellow-100 p-4 rounded-lg col-span-2">
          <h3 className="font-semibold mb-2">Recommendations</h3>
          {renderItem(recommendations)}
        </div>
      </div>
    </div>
  );
}
