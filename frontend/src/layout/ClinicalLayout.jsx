import { Outlet, Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { fetchPatients } from "../api/patients";

export default function ClinicalLayout({
  facilityName = "VitalMesh Medical Center",
}) {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchPatients();
        console.log("Fetched patients:", data); // 👈 check what comes back
        setPatients(data);
      } catch (err) {
        console.error("Failed to fetch patients", err);
        setPatients([]);
      }
    }
    load();
  }, []);

  const handleNewPatient = () => {
    const newId = Math.floor(Math.random() * 1000000); // random ID placeholder
    navigate(`/clinical/patient/${newId}`);
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Top Header */}
      <header className="bg-gradient-to-b from-blue-100 to-gray-400 p-4">
        <h1 className="text-2xl text-gray-800 font-bold">{facilityName}</h1>
      </header>

      {/* Content Area */}
      <div className="flex flex-1">
        {/* Sidebar */}
        <div className="w-64 bg-gray-100 p-4">
          <h2 className="text-xl font-bold mb-4">Patients</h2>
          <input
            type="text"
            placeholder="Search (DOB / Last Name)"
            className="w-full p-2 border rounded mb-4"
          />
          <ul className="space-y-2">
            <li>
              <Link to="/clinical/dashboard">📊 Dashboard</Link>
            </li>
            {Array.isArray(patients) &&
              patients.map((p) => (
                <li key={p.id}>
                  <Link to={`/clinical/patient/${p.id}`}>
                    🧑 {p?.patient_info?.name || "Unnamed"} ({p.id})
                  </Link>
                </li>
              ))}
          </ul>
          <button
            onClick={handleNewPatient}
            className="mt-6 w-full bg-green-500 text-white py-2 rounded"
          >
            ➕ New Patient
          </button>
        </div>

        {/* Main */}
        <div className="flex-1 p-6 bg-white overflow-y-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
