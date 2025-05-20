import React, { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { GrClose } from "react-icons/gr";
import { useNavigate } from "react-router-dom";

const Topics = () => {
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  const [topics, setTopics] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState(null);
  const navigate = useNavigate();

  const token = Cookies.get("token");

  useEffect(() => {
    if (token) {
      fetch(`${API_BASE_URL}/category`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => response.json())
        .then((data) => setCategories([{ id: "All", name: "All" }, ...data]))
        .catch((error) => console.error("Error fetching categories:", error));
    }
  }, [token]);

  const fetchTopics = () => {
    if (!token) return;
    let topicUrl = `${API_BASE_URL}/topic`;
    if (selectedCategory !== "All") {
      topicUrl += `?category_name=${selectedCategory}`;
    }
    fetch(topicUrl, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setTopics(data);
        } else {
          setTopics([]);
        }
      })
      .catch((error) => console.error("Error fetching topics:", error));
  };

  useEffect(() => {
    fetchTopics();
  }, [selectedCategory]);

  const filteredTopics = topics.filter((topic) =>
    topic.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleTopicClick = (topic) => {
    setSelectedTopic(topic);
  };

  const handleReturn = () => {
    setSelectedTopic(null);
    setSelectedDuration(null);
  };

  const startConversation = () => {
    if (!selectedTopic) {
      alert("Please select a topic.");
      return;
    }
  
    if (!selectedDuration) {
      alert("Please select a duration.");
      return;
    }
  
    const queryParams = new URLSearchParams({
      topic_id: selectedTopic.id,
      duration: selectedDuration,
    }).toString();
  
    navigate(`/chat?${queryParams}`);
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-slate-50 text-black p-6">
      {/* Topic Details Box */}
      {selectedTopic && (
        <div className="fixed inset-0 flex items-center justify-center p-5 bg-black bg-opacity-50 z-50">
          <div className="w-full md:w-1/3 bg-gray-300 p-6 rounded-lg shadow-md relative">
            <button
              onClick={handleReturn}
              className="absolute top-2 right-2 text-black"
            >
              <GrClose />
            </button>
            <h3 className="text-2xl font-bold mb-4">Topic Details</h3>
            <div className="m-3">
              <p>
                <strong>Topic:</strong>
                <br /> {selectedTopic.name}
              </p>
              <p>
                <strong>Description:</strong>
                <br /> {selectedTopic.description}
              </p>
              <div>
                <strong>Duration:</strong>
                <br />
                <div className="flex space-x-4 mt-2">
                  {[1, 5, 10].map((duration) => (
                    <button
                      key={duration}
                      className={`p-5 bg-gray-400 text-black rounded-full hover:bg-gray-600 border border-white shadow ${
                        selectedDuration === duration ? "bg-gray-600" : ""
                      }`}
                      onClick={() => setSelectedDuration(duration)}
                    >
                      {duration} mins
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex justify-center mt-4">
                <button
                  className="px-4 py-2 bg-neutral-500 text-white rounded-md hover:bg-neutral-600"
                  onClick={startConversation}
                  disabled={!selectedDuration}
                >
                  Start
                </button>
              </div>
              
            </div>
          </div>
        </div>
      )}
      <div className="flex flex-col w-full">
        <h1 className="text-4xl font-bold mb-6">Topics</h1>

        {/* Search and Filter Section */}
        <div className="mt-6 flex flex-col md:flex-row gap-10 items-center w-full max-w-7xl">
          <input
            type="text"
            placeholder="Search topics..."
            className="p-2 px-5 w-full md:w-1/2 bg-gray-300 text-black rounded"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <select
            className="p-2 bg-gray-300 text-black rounded"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map((category) => (
              <option key={category.id} value={category.name}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center justify-center mt-4">
          <hr className="w-full border-gray-300" />
        </div>
        {/* Topics Table */}
        <div className="mt-10 w-full max-w-full overflow-x-auto">
          <h2 className="text-2xl font-semibold mb-4">Your Topics</h2>
          <table className="min-w-full bg-gray-200 rounded-lg overflow-hidden">
            <thead>
              <tr className="bg-gray-300 text-black">
                <th className="p-3">Topic</th>
                <th className="p-3">Description</th>
                <th className="p-3">Your Score</th>
                <th className="p-3">High Score</th>
              </tr>
            </thead>
            <tbody>
              {filteredTopics.length > 0 ? (
                filteredTopics.map((topic, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-700 text-left cursor-pointer"
                    onClick={() => handleTopicClick(topic)}
                  >
                    <td className="p-3">{topic.name}</td>
                    <td className="p-3">{topic.description}</td>
                    <td className="p-3">{topic.your_score}</td>
                    <td className="p-3">{topic.high_score}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center p-4">
                    No topics available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Topics;