import React, { useEffect, useState } from "react";
import Cookies from "js-cookie";

const Home = () => {
  const [stats, setStats] = useState({
    total_session: "",
    avg_score: "",
    high_score: "",
  });

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  const [topics, setTopics] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = Cookies.get("token");

  useEffect(() => {
    if (token) {
      // Fetch user stats
      fetch(`${API_BASE_URL}/stats`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => response.json())
        .then((data) => setStats(data))
        .catch((error) => console.error("Error fetching stats:", error));

      // Fetch categories
      fetch(`${API_BASE_URL}/category`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => response.json())
        .then((data) => setCategories([{ id: "All", name: "All" }, ...data]))
        .catch((error) => console.error("Error fetching categories:", error));
    }
  }, [token]);

  // Function to fetch topics based on selected category
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

  // Fetch topics when the category changes
  useEffect(() => {
    fetchTopics();
  }, [selectedCategory]);

  // Filter topics based on search query
  const filteredTopics = topics.filter((topic) =>
    topic.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-neutral-100 text-black p-6">
      <h1 className="text-4xl font-bold mb-6">Welcome to Lexi AI</h1>
      <div className="flex items-center justify-center mt-4">
        <hr className="w-full border-gray-300" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        <StatCard title="Your Total Sessions" value={stats.total_session} />
        <StatCard title="Your Average Score" value={stats.avg_score} />
        <StatCard title="Your Highest Score" value={stats.high_score} />
      </div>
      {/* Search and Filter Section */}
      <div className="mt-6 flex flex-col md:flex-row gap-4 items-center w-full max-w-4xl">
        <input
          type="text"
          placeholder="Search by topic..."
          className="p-2 w-full md:w-1/2 bg-neutral-200 text-black rounded"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <select
          className="p-2 bg-neutral-200 text-black rounded"
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
      {/* Topic Table */}

      <div className="mt-10 w-full max-w-full overflow-x-auto">
        <h2 className="text-2xl font-semibold">Your Topics</h2>
        <div className="flex items-center justify-center m-4">
        <hr className="w-full border-gray-300" />
      </div>
        <table className="min-w-full bg-neutral-200 rounded-lg overflow-hidden">
          <thead>
            <tr className="bg-neutral-400 text-white text-left">
              <th className="p-3">Topic</th>
              <th className="p-3">Description</th>
              <th className="p-3">Your Score</th>
              <th className="p-3">High Score</th>
            </tr>
          </thead>
          <tbody>
            {filteredTopics.length > 0 ? (
              filteredTopics.map((topic, index) => (
                <tr key={index} className="border-b border-gray-700 text-left">
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
  );
};

const StatCard = ({ title, value }) => (
  <div className="bg-neutral-300 p-6 rounded-lg shadow-md text-center">
    <h2 className="text-2xl font-semibold mb-2">{title}</h2>
    <p className="text-3xl font-bold">{value}</p>
  </div>
);

export default Home;
