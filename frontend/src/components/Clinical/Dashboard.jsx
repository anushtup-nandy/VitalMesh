import { LineChart, Line, CartesianGrid, XAxis, YAxis } from "recharts";

const data = [
  { name: "9am", wait: 5 },
  { name: "10am", wait: 8 },
  { name: "11am", wait: 4 },
];

export default function Dashboard() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Clinic Analytics</h2>
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-blue-100 p-4 rounded-lg">Avg Wait: 6 min</div>
        <div className="bg-green-100 p-4 rounded-lg">Patients Waiting: 3</div>
        <div className="bg-yellow-100 p-4 rounded-lg">Daily Visits: 12</div>
      </div>
      <div className="mt-8">
        <LineChart width={500} height={300} data={data}>
          <Line type="monotone" dataKey="wait" stroke="#8884d8" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="name" />
          <YAxis />
        </LineChart>
      </div>
    </div>
  );
}
