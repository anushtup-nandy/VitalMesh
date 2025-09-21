// import { useEffect, useState, useRef } from "react";
// import { Link } from "react-router-dom";
// import { startVoiceAgent, stopVoiceAgent, getAgentStatus } from "../../api/voiceAgent";

// export default function PatientVoice() {
//   const [isActive, setIsActive] = useState(false);
//   const [isStarting, setIsStarting] = useState(false);
//   const [statusMessage, setStatusMessage] = useState("Checking agent status...");
//   const hasStarted = useRef(false);

//   useEffect(() => {
//     if (hasStarted.current) return;
    
//     const initializeAgent = async () => {
//       try {
//         setIsStarting(true);
//         hasStarted.current = true;
        
//         // First, check if agent is already running
//         console.log("Checking agent status...");
//         const statusResponse = await getAgentStatus();
//         console.log("Agent status response:", statusResponse);
        
//         if (statusResponse.status === "running" || statusResponse.status === "active") {
//           console.log("Agent is already running");
//           setIsActive(true);
//           setStatusMessage("Speaking with AI agent...");
//           setIsStarting(false);
//           return;
//         }
        
//         // If not running, try to start it
//         console.log("Starting voice agent...");
//         setStatusMessage("Starting agent...");
//         const startResponse = await startVoiceAgent();
//         console.log("Start agent response:", startResponse);
        
//         if (startResponse.status === "already_running" || startResponse.status === "started") {
//           console.log("Voice agent is now active");
//           setIsActive(true);
//           setStatusMessage("Speaking with AI agent...");
//         } else {
//           console.error("Unexpected start response:", startResponse);
//           setIsActive(false);
//           setStatusMessage("Failed to start agent");
//           hasStarted.current = false;
//         }
        
//       } catch (err) {
//         console.error("Failed to initialize voice agent:", err);
//         setIsActive(false);
//         setStatusMessage("Agent connection failed");
//         hasStarted.current = false;
//       } finally {
//         setIsStarting(false);
//       }
//     };

//     initializeAgent();

//     // Cleanup function
//     return () => {
//       if (isActive) {
//         stopVoiceAgent().catch(console.error);
//       }
//     };
//   }, []);

//   const handleEndConversation = async () => {
//     try {
//       setIsActive(false);
//       setIsStarting(false);
//       setStatusMessage("Stopping agent...");
//       hasStarted.current = false;
      
//       await stopVoiceAgent();
//       console.log("Voice agent stopped");
//       setStatusMessage("Agent stopped");
//     } catch (err) {
//       console.error("Failed to stop voice agent:", err);
//       setStatusMessage("Failed to stop agent");
//     }
//   };

//   // Determine visual state
//   const getCircleState = () => {
//     if (isActive) return { bg: "bg-green-400 animate-pulse", emoji: "🎤" };
//     if (isStarting) return { bg: "bg-yellow-400 animate-spin", emoji: "⏳" };
//     return { bg: "bg-gray-200", emoji: "😴" };
//   };

//   const circleState = getCircleState();

//   return (
//     <div className="h-screen flex flex-col items-center justify-center bg-white">
//       {/* Animated Circle */}
//       <div className={`w-48 h-48 rounded-full flex items-center justify-center mb-6 transition-all duration-300 ${circleState.bg}`}>
//         <span className="text-white text-3xl">
//           {circleState.emoji}
//         </span>
//       </div>

//       <p className="mb-4 text-lg font-medium">
//         {statusMessage}
//       </p>

//       {/* Debug info (remove in production) */}
//       <div className="mb-4 text-sm text-gray-500">
//         <p>Active: {isActive.toString()}</p>
//         <p>Starting: {isStarting.toString()}</p>
//       </div>

//       {/* End Conversation */}
//       <Link
//         to="/patient/report"
//         className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg disabled:opacity-50 transition-colors"
//         onClick={handleEndConversation}
//         style={{ pointerEvents: isStarting ? 'none' : 'auto' }}
//       >
//         End Conversation
//       </Link>
//     </div>
//   );
// }

import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import { startVoiceAgent, stopVoiceAgent, getAgentStatus } from "../../api/voiceAgent";

export default function PatientVoice() {
  const [isActive, setIsActive] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Checking agent status...");
  const hasStarted = useRef(false);

  useEffect(() => {
    if (hasStarted.current) return;
    
    const initializeAgent = async () => {
      try {
        setIsStarting(true);
        hasStarted.current = true;
        
        // First, check if agent is already running
        console.log("Checking agent status...");
        const statusResponse = await getAgentStatus();
        console.log("Agent status response:", statusResponse);
        
        if (statusResponse.status === "running") {
          console.log("Agent is already running");
          setIsActive(true);
          setStatusMessage("Speaking with AI agent...");
          setIsStarting(false);
          return;
        }
        
        // If not running, try to start it
        console.log("Starting voice agent...");
        setStatusMessage("Starting agent...");
        const startResponse = await startVoiceAgent();
        console.log("Start agent response:", startResponse);
        
        // Accept the correct response formats from your backend
        if (startResponse.status === "already_running" || 
            startResponse.status === "started" || 
            startResponse.status === "starting") {
          console.log("Voice agent is now active");
          setIsActive(true);
          setStatusMessage("Speaking with AI agent...");
        } else {
          console.error("Unexpected start response:", startResponse);
          setIsActive(false);
          setStatusMessage(`Agent status: ${startResponse.status || 'Unknown'}`);
          hasStarted.current = false;
        }
        
      } catch (err) {
        console.error("Failed to initialize voice agent:", err);
        setIsActive(false);
        setStatusMessage("Agent connection failed");
        hasStarted.current = false;
      } finally {
        setIsStarting(false);
      }
    };

    initializeAgent();

    // Cleanup function
    return () => {
      if (isActive) {
        stopVoiceAgent().catch(console.error);
      }
    };
  }, []);

  const handleEndConversation = async () => {
    try {
      setIsActive(false);
      setIsStarting(false);
      setStatusMessage("Stopping agent...");
      hasStarted.current = false;
      
      await stopVoiceAgent();
      console.log("Voice agent stopped");
      setStatusMessage("Agent stopped");
    } catch (err) {
      console.error("Failed to stop voice agent:", err);
      setStatusMessage("Failed to stop agent");
    }
  };

  // Determine visual state
  const getCircleState = () => {
    if (isActive) return { bg: "bg-green-400 animate-pulse", emoji: "🎤" };
    if (isStarting) return { bg: "bg-yellow-400 animate-spin", emoji: "⏳" };
    return { bg: "bg-gray-200", emoji: "😴" };
  };

  const circleState = getCircleState();

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-white">
      {/* Animated Circle */}
      <div className={`w-48 h-48 rounded-full flex items-center justify-center mb-6 transition-all duration-300 ${circleState.bg}`}>
        <span className="text-white text-3xl">
          {circleState.emoji}
        </span>
      </div>

      <p className="mb-4 text-lg font-medium">
        {statusMessage}
      </p>

      {/* Debug info (remove in production) */}
      <div className="mb-4 text-sm text-gray-500">
        <p>Active: {isActive.toString()}</p>
        <p>Starting: {isStarting.toString()}</p>
      </div>

      {/* End Conversation */}
      <Link
        to="/patient/report"
        className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg disabled:opacity-50 transition-colors"
        onClick={handleEndConversation}
        style={{ pointerEvents: isStarting ? 'none' : 'auto' }}
      >
        End Conversation
      </Link>
    </div>
  );
}