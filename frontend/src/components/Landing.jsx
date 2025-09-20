import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-100 to-white">
      <h1 className="text-3xl font-bold mb-8">Welcome to VitalMesh</h1>
      <div className="flex gap-6">
        <Link
          to="/patient"
          className="bg-green-500 text-white px-6 py-4 rounded-xl shadow hover:bg-green-600"
        >
          Patient Side
        </Link>
        <Link
          to="/clinical/login"
          className="bg-blue-500 text-white px-6 py-4 rounded-xl shadow hover:bg-blue-600"
        >
          Clinical Side
        </Link>
      </div>
    </div>
  );
}
