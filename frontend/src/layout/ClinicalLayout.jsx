// <project-root>/frontend/src/layout/ClinicalLayout.jsx
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
        console.log("Fetched patients:", data);
        setPatients(data);
      } catch (err) {
        console.error("Failed to fetch patients", err);
        setPatients([]);
      }
    }
    load();
  }, []);

  const handleNewPatient = () => {
    const newId = Math.floor(Math.random() * 1000000);
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
          <h2 className="text-xl font-bold mb-4">Navigation</h2>
          
          {/* Search */}
          <input
            type="text"
            placeholder="Search (DOB / Last Name)"
            className="w-full p-2 border rounded mb-4"
          />
          
          {/* Main Navigation */}
          <ul className="space-y-2 mb-6">
            <li>
              <Link 
                to="/clinical/dashboard" 
                className="flex items-center space-x-2 p-2 rounded hover:bg-gray-200 transition-colors"
              >
                <span>📊</span>
                <span>Dashboard</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/clinical/chatbot" 
                className="flex items-center space-x-2 p-2 rounded hover:bg-gray-200 transition-colors"
              >
                <span>🩺</span>
                <span>Dr. VitalMesh (AI)</span>
              </Link>
            </li>
          </ul>

          {/* Patients Section */}
          <div className="border-t border-gray-300 pt-4">
            <h3 className="font-semibold mb-3 text-gray-700">Patients</h3>
            <ul className="space-y-2 max-h-64 overflow-y-auto">
              {Array.isArray(patients) &&
                patients.map((p) => (
                  <li key={p.id}>
                    <Link 
                      to={`/clinical/patient/${p.id}`}
                      className="flex items-center space-x-2 p-2 rounded hover:bg-gray-200 transition-colors text-sm"
                    >
                      <span>🧑</span>
                      <span className="truncate">
                        {p?.patient_info?.name || "Unnamed"} ({p.id})
                      </span>
                    </Link>
                  </li>
                ))}
            </ul>
          </div>

          {/* New Patient Button */}
          <button
            onClick={handleNewPatient}
            className="mt-6 w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded transition-colors flex items-center justify-center space-x-2"
          >
            <span>➕</span>
            <span>New Patient</span>
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 bg-white overflow-y-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
}