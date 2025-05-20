// import React, { useState, useEffect, useRef } from "react";

// const CommunicationPage = ({ topicId, duration }) => {
//   const [messages, setMessages] = useState([]);
//   const [isListening, setIsListening] = useState(false);
//   const [websocket, setWebSocket] = useState(null);
//   const [conversationStarted, setConversationStarted] = useState(false);
//   const [isError, setIsError] = useState(false);
//   const audioRef = useRef(null);

//   useEffect(() => {
//     // Establish WebSocket connection
//     const ws = new WebSocket(`ws://localhost/conversation?topic_id=${topicId}&duration=${duration}`);

//     ws.onopen = () => {
//       console.log("WebSocket connection established.");
//     };

//     ws.onmessage = (event) => {
//       const data = JSON.parse(event.data);
//       if (data.type === "AI_RESPONSE") {
//         setMessages((prevMessages) => [...prevMessages, { type: "AI", text: data.message }]);
//         speakResponse(data.message); // Speak out the AI's response
//       } else if (data.type === "ERROR") {
//         setIsError(true);
//         alert("Error: " + data.message);
//       }
//     };

//     ws.onclose = () => {
//       console.log("WebSocket connection closed.");
//     };

//     setWebSocket(ws);

//     return () => {
//       if (ws) ws.close();
//     };
//   }, [topicId, duration]);

//   const startConversation = () => {
//     if (websocket) {
//       setConversationStarted(true);
//       websocket.send(JSON.stringify({ type: "START_CONVERSATION" }));
//     }
//   };

//   const stopConversation = () => {
//     if (websocket) {
//       websocket.send(JSON.stringify({ type: "STOP_CONVERSATION" }));
//       setConversationStarted(false);
//     }
//   };

//   const handleAudioInput = async () => {
//     setIsListening(true);
//     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//     const mediaRecorder = new MediaRecorder(stream);

//     mediaRecorder.ondataavailable = async (event) => {
//       const audioData = event.data;
//       sendAudioToServer(audioData);
//     };

//     mediaRecorder.start();
//   };

//   const sendAudioToServer = (audioData) => {
//     if (websocket) {
//       const reader = new FileReader();
//       reader.onload = () => {
//         const audioBuffer = reader.result;
//         websocket.send(JSON.stringify({ type: "USER_AUDIO", audio: audioBuffer }));
//       };
//       reader.readAsArrayBuffer(audioData);
//     }
//   };

//   const speakResponse = (responseText) => {
//     const utterance = new SpeechSynthesisUtterance(responseText);
//     window.speechSynthesis.speak(utterance);
//   };

//   return (
//     <div>
//       <h1>Talk to the AI about {topicId}</h1>

//       {!conversationStarted ? (
//         <button onClick={startConversation}>Start Conversation</button>
//       ) : (
//         <button onClick={stopConversation}>End Conversation</button>
//       )}

//       {isError && <p style={{ color: "red" }}>There was an error with the conversation.</p>}

//       <div>
//         {messages.map((msg, index) => (
//           <div key={index}>
//             <strong>{msg.type}:</strong> {msg.text}
//           </div>
//         ))}
//       </div>

//       {isListening ? (
//         <div>Listening...</div>
//       ) : (
//         <button onClick={handleAudioInput}>Start Talking</button>
//       )}
//     </div>
//   );
// };

// export default CommunicationPage;

// import React, { useEffect, useState, useRef } from "react";

// const CommunicationPage = ({ userToken }) => {
//   const [messages, setMessages] = useState([]);
//   const [topicId, setTopicId] = useState("");
//   const [duration, setDuration] = useState(2); // minutes
//   const ws = useRef(null);

//   const handleStart = () => {
//     const url = `ws://localhost:8000/conversation?topic_id=${topicId}&duration=${duration}&token=${userToken}`;
// console.log("WebSocket URL:", url); // Log the WebSocket URL

//     ws.current = new WebSocket(url);

//     ws.current.onopen = () => {
//       console.log("✅ WebSocket connected");
//     };

//     ws.current.onmessage = (event) => {
// console.log("📥 Message:", event.data); // Log incoming messages
//       setMessages((prev) => [...prev, { type: "ai", text: event.data }]);
//     };

//     ws.current.onclose = (event) => {
//       console.warn("⚠️ WebSocket closed:", event); // Log WebSocket closure
//     };

//     ws.current.onerror = (error) => {
//       console.error("❌ WebSocket error:", error); // Log WebSocket errors
//     };
//   };

//   return (
//     <div className="p-4 max-w-2xl mx-auto">
//       <h1 className="text-2xl font-bold mb-4">Start a Conversation</h1>
//       <div className="flex gap-2 mb-4">
//         <input
//           type="text"
//           placeholder="Topic ID"
//           value={topicId}
//           onChange={(e) => setTopicId(e.target.value)}
//           className="border p-2 flex-1"
//         />
//         <input
//           type="number"
//           placeholder="Duration (min)"
//           value={duration}
//           onChange={(e) => setDuration(Number(e.target.value))}
//           className="border p-2 w-32"
//         />
//         <button onClick={handleStart} className="bg-blue-600 text-white px-4 py-2 rounded">
//           Start
//         </button>
//       </div>

//       <div className="border rounded p-4 h-96 overflow-y-auto bg-gray-100">
//         {messages.map((msg, i) => (
//           <div key={i} className={`mb-2 ${msg.type === "ai" ? "text-blue-700" : "text-black"}`}>
//             {msg.text}
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };

// export default CommunicationPage;

import React, { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import Cookies from "js-cookie";

const CommunicationPage = () => {
  const [messages, setMessages] = useState([]);
  const socketRef = useRef(null);
  const location = useLocation();
  const token = Cookies.get("token");

  const queryParams = new URLSearchParams(location.search);
  const topicId = queryParams.get("topic_id");
  const duration = queryParams.get("duration");

  useEffect(() => {
    if (!topicId || !duration || !token) return;

    const wsUrl = `ws://192.168.0.105:8000/conversation?topic_id=${topicId}&duration=${duration}`;
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      console.log("WebSocket connected");
      // Send token as header workaround (if backend requires it this way)
      socketRef.current.send(
        JSON.stringify({ type: "auth", token: `Bearer ${token}` })
      );
    };

    socketRef.current.onmessage = (event) => {
      console.log("Received:", event.data);
      setMessages((prev) => [...prev, { sender: "ai", text: event.data }]);
    };

    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket closed");
    };

    return () => {
      socketRef.current.close();
    };
  }, [topicId, duration, token]);

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">AI Conversation</h2>
      <div className="border rounded p-3 h-80 overflow-y-scroll bg-gray-50">
        {messages.map((msg, index) => (
          <div key={index} className="mb-2">
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommunicationPage;
