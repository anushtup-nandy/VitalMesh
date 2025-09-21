import { useState, useEffect, useRef } from "react";
import { sendChatMessage, refreshChatbotData, getChatbotStatus } from "../api/chatbot";

export default function MedicalChatbot() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      content: "👋 Hello! I'm Dr. VitalMesh, your AI medical assistant. I have access to comprehensive patient EHR data and can help answer questions about your patients. How can I assist you today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatbotStatus, setChatbotStatus] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Get chatbot status on component mount
    async function checkStatus() {
      try {
        const status = await getChatbotStatus();
        setChatbotStatus(status);
      } catch (error) {
        console.error("Failed to get chatbot status:", error);
      }
    }
    checkStatus();
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage(inputMessage);
      
      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.success ? response.response : `Error: ${response.error || "Unknown error occurred"}`,
        timestamp: new Date(),
        error: !response.success
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: "Sorry, I'm having trouble connecting right now. Please check that the backend is running and try again.",
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRefreshData = async () => {
    try {
      setIsLoading(true);
      const result = await refreshChatbotData();
      
      const refreshMessage = {
        id: Date.now(),
        type: "bot",
        content: `🔄 ${result.message}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, refreshMessage]);
      
      // Update status
      const status = await getChatbotStatus();
      setChatbotStatus(status);
    } catch (error) {
      const errorMessage = {
        id: Date.now(),
        type: "bot",
        content: "Failed to refresh data. Please try again.",
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(timestamp);
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold">🩺 Dr. VitalMesh</h2>
            <p className="text-blue-100 text-sm">AI Medical Assistant</p>
          </div>
          <div className="flex items-center space-x-4">
            {chatbotStatus && (
              <div className="text-right text-sm">
                <div className={`font-medium ${chatbotStatus.status === 'available' ? 'text-green-200' : 'text-red-200'}`}>
                  Status: {chatbotStatus.status}
                </div>
                <div className="text-blue-200">
                  Patients: {chatbotStatus.patient_count}
                </div>
              </div>
            )}
            <button
              onClick={handleRefreshData}
              disabled={isLoading}
              className="bg-blue-500 hover:bg-blue-400 disabled:bg-blue-700 px-3 py-1 rounded text-sm font-medium transition-colors"
            >
              🔄 Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === "user"
                  ? "bg-blue-600 text-white"
                  : message.error
                  ? "bg-red-100 text-red-800 border border-red-300"
                  : "bg-white text-gray-800 border border-gray-200 shadow-sm"
              }`}
            >
              <div className="whitespace-pre-wrap break-words">{message.content}</div>
              <div className={`text-xs mt-1 opacity-70 ${
                message.type === "user" ? "text-blue-100" : "text-gray-500"
              }`}>
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-gray-600">Dr. VitalMesh is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex space-x-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask me anything about your patients... (e.g., 'Show me patient P001's latest vitals' or 'Which patients have hypertension?')"
            className="flex-1 border border-gray-300 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <span>💬</span>
            <span>Send</span>
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}