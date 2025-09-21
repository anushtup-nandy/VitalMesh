// <project-root>/frontend/src/router.jsx
import { createBrowserRouter } from "react-router-dom";
import Landing from "./components/Landing";
import PatientStart from "./components/Patient/PatientStart";
import PatientVoice from "./components/Patient/PatientVoice";
import PatientReport from "./components/Patient/PatientReport";
import Login from "./components/Clinical/Login";
import ClinicalLayout from "./layout/ClinicalLayout";
import Dashboard from "./components/Clinical/Dashboard";
import PatientDetail from "./components/Clinical/PatientDetail";
import MedicalChatbot from "./components/MedicalChatbot";

export const router = createBrowserRouter([
  { path: "/", element: <Landing /> },
  { path: "/patient", element: <PatientStart /> },
  { path: "/patient/voice", element: <PatientVoice /> },
  { path: "/patient/report", element: <PatientReport /> },
  { path: "/clinical/login", element: <Login /> },
  {
    path: "/clinical",
    element: <ClinicalLayout />,
    children: [
      { path: "dashboard", element: <Dashboard /> },
      { path: "chatbot", element: <MedicalChatbot /> },
      { path: "patient/:patientId", element: <PatientDetail /> },
    ],
  },
]);