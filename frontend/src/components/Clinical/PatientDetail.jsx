import { useParams } from "react-router-dom";

export default function PatientDetail() {
  const { patientId } = useParams();

  // later: fetch patient data from backend with patientId
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Patient {patientId}</h2>
      <div className="bg-white shadow p-4 rounded-lg mb-6">
        <p>
          <strong>Name:</strong> Placeholder Name
        </p>
        <p>
          <strong>DOB:</strong> Placeholder DOB
        </p>
        <p>
          <strong>Condition:</strong> Placeholder condition
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-100 p-4 rounded-lg">Vitals Graph</div>
        <div className="bg-green-100 p-4 rounded-lg">EHR Notes</div>
      </div>
    </div>
  );
}
