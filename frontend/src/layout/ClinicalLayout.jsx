import { Outlet, Link, useNavigate } from "react-router-dom";

export default function ClinicalLayout({
  facilityName = "VitalMesh Medical Center",
}) {
  const navigate = useNavigate();

  const handleNewPatient = () => {
    const newId = Math.floor(Math.random() * 1000000); // random patient ID
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
            <li>
              <Link to="/clinical/patient/1">Patient Example</Link>
            </li>
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
