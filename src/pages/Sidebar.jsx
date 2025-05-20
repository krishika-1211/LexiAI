import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FaBars,
  FaTimes,
  FaHome,
  FaBook,
  FaHistory,
  FaMoneyBill,
  FaSignOutAlt,
  FaUser,
} from "react-icons/fa";
import { SlArrowDown } from "react-icons/sl";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = Cookies.get("token");
    if (token) {
      const decoded = jwtDecode(token);
      setEmail(decoded.email);
    }
  }, []);

  const handleLogout = () => {
    Cookies.remove("token");
    navigate("/");
  };

  const truncatedEmail = email.length > 6 ? `${email.slice(0, 6)}...` : email;

  return (
    <div className="flex">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full bg-neutral-500 text-white w-64 p-5 space-y-6 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-64"
        } md:translate-x-0 flex flex-col justify-between`}
      >
        <div>
          <Link
            to="/"
            className="text-4xl font-bold"
            style={{ fontFamily: "Poppins, sans-serif" }}
          >
            <h1>LexiAI</h1>
          </Link>
          <hr className="w-full border-gray-300 mt-4" />

          <nav className="flex flex-col space-y-4 mt-6">
            <Link
              to="/home"
              className="flex items-center space-x-2 p-3 hover:bg-neutral-400 text-xl rounded"
            >
              <FaHome />
              <span>Home</span>
            </Link>
            <Link
              to="/topic"
              className="flex items-center space-x-2 p-3 hover:bg-neutral-400 text-xl rounded"
            >
              <FaBook />
              <span>Topic</span>
            </Link>
            <Link
              to="/history"
              className="flex items-center space-x-2 p-3 hover:bg-neutral-400 text-xl rounded"
            >
              <FaHistory />
              <span>History</span>
            </Link>
            <Link
              to="/billing"
              className="flex items-center space-x-2 p-3 hover:bg-neutral-400 text-xl rounded"
            >
              <FaMoneyBill />
              <span>Billing</span>
            </Link>
          </nav>
        </div>

        {/* User Icon & Dropdown */}
        <div className="relative flex flex-col items-center">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-neutral-400"
          >
            <FaUser
              size={20}
              className="w-12 h-12 rounded-full border border-gray-400"
            />
            <div className="flex flex-col">
              <span className="text-white mt-2">{truncatedEmail}</span>
            </div>
            <SlArrowDown
              className={`transform transition-transform ${
                showDropdown ? "rotate-180" : ""
              }`}
            />
          </button>

          {showDropdown && (
            <div className="absolute bottom-16 right-0 w-56 bg-neutral-100 text-black shadow-lg rounded-md p-3">
              <p className="text-gray-700 font-semibold px-3">Hi, {email}!</p>
              <hr className="my-2 border-gray-300" />
              <Link
                to="/billing"
                className="flex items-center space-x-2 px-3 py-2 hover:bg-neutral-400 rounded-md"
              >
                📜 <span>Manage subscription</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 text-red-600 hover:bg-gray-100 rounded-md w-full"
              >
                <FaSignOutAlt />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 bg-gray-900 text-white p-2 rounded md:hidden"
      >
        {isOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
      </button>
    </div>
  );
};

export default Sidebar;
