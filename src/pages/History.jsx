import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

const History = () => {
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  const navigate = useNavigate();
  const [historyData, setHistoryData] = useState([]);
  const token = Cookies.get("token");

  useEffect(() => {
    if (!token) return;

    fetch(`${API_BASE_URL}/history`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setHistoryData(data);
        } else {
          setHistoryData([]);
        }
      })
      .catch((error) => console.error("Error fetching history:", error));
  }, [token]);

  return (
    <div className="flex flex-col min-h-screen bg-neutral-100 text-black p-6">
      <h1 className="text-4xl font-bold mt-1">History</h1>

      {/* Show Table If Data Exists */}
      {historyData.length > 0 ? (
        <div className="mt-10 w-full overflow-x-auto">
          <table className="min-w-full bg-neutral-200 rounded-lg overflow-hidden">
            <thead>
              <tr className="bg-neutral-400 text-white text-left">
                <th className="p-3">ID</th>
                <th className="p-3">Topic</th>
                <th className="p-3">Mins</th>
                <th className="p-3">Score</th>
              </tr>
            </thead>
            <tbody>
              {historyData.map((item, index) => (
                <tr
                  key={index}
                  className="border-b border-gray-700 text-left"
                >
                  <td className="p-3">{item.id}</td>
                  <td className="p-3">{item.topic}</td>
                  <td className="p-3">{item.mins}</td>
                  <td className="p-3">{item.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        // Show "Get Started" Button If No Data
        <div className="mt-20 flex flex-col items-center">
          <p className="text-lg">No history available</p>
          <button
            onClick={() => navigate("/topic")}
            className="mt-4 px-6 py-3 bg-neutral-400 text-white text-lg font-semibold rounded-lg hover:bg-neutral-500 transition"
          >
            Get Started
          </button>
        </div>
      )}
    </div>
  );
};

export default History;
