import { Outlet, Link } from "react-router-dom";

export default function ClinicalLayout() {
  return (
    <div className="flex h-screen">
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
      </div>
      {/* Main */}
      <div className="flex-1 p-6 bg-white overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
}
