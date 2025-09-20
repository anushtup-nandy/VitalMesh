import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();
  const handleLogin = () => {
    navigate("/clinical/dashboard");
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-blue-50">
      <h2 className="text-2xl font-bold mb-6">Clinical Login</h2>
      <div className="bg-white p-6 rounded-lg shadow-md w-80 flex flex-col gap-4">
        <input className="border p-2 rounded" placeholder="Username" />
        <input
          className="border p-2 rounded"
          type="password"
          placeholder="Password"
        />
        <button
          onClick={handleLogin}
          className="bg-blue-500 text-white py-2 rounded"
        >
          Login
        </button>
      </div>
    </div>
  );
}
