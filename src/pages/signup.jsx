import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import { FcGoogle } from "react-icons/fc";

const Signup = () => {
  const navigate = useNavigate();
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  const [formData, setFormData] = useState({
    firstname: "",
    lastname: "",
    email: "",
    password: "",
  });

  const [errorMessage, setErrorMessage] = useState("");
  const [errors, setErrors] = useState({
    firstname: "",
    lastname: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData((prevFormData) => ({
      ...prevFormData,
      [e.target.name]: e.target.value,
    }));
  };

  const validateInputs = () => {
    const newErrors = {
      firstname: "",
      lastname: "",
      email: "",
      password: "",
    };
    let isValid = true;

    if (!formData.firstname.trim()) {
      newErrors.firstname = "First name is required";
      isValid = false;
    }

    if (!formData.lastname.trim()) {
      newErrors.lastname = "Last name is required";
      isValid = false;
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
      isValid = false;
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = "Invalid email format";
        isValid = false;
      }
    }

    if (!formData.password.trim()) {
      newErrors.password = "Password is required";
      isValid = false;
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateInputs()) {
      setErrorMessage(
        "Ensure all fields are correctly filled out and resubmit."
      );
      return;
    }
    try {
      const res = await axios.post(`${API_BASE_URL}/signup`, formData);
      console.log("SignUp Success:", res.data);
      Cookies.set("token", res.data.token);
      console.log(res.data.token);
      setErrorMessage("");
      navigate("/home");
    } catch (error) {
      console.error("Error Details:", error);
      if (error.response && error.response.data) {
        const errorData = error.response.data;
        setErrors({
          firstname: errorData.firstname ? errorData.firstname.join(" ") : "",
          lastname: errorData.lastname ? errorData.lastname.join(" ") : "",
          email: errorData.email ? errorData.email.join(" ") : "",
          password: errorData.password ? errorData.password.join(" ") : "",
        });
        setErrorMessage("Signup failed.");
      } else {
        setErrorMessage("Error occurred. Please try again.");
      }
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/auth/google`, {
        params: {
          redirect_uri: "http://localhost:3000/auth-callback", // Ensure this matches the URI in Google Cloud Console
        },
      });
      if (res.status === 200 && res.data.auth_url) {
        window.location.href = res.data.auth_url;
      }
    } catch (error) {
      console.error("Google Login Error:", error);
      setErrorMessage("Failed to authenticate with Google.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold text-center">Sign Up</h1>
        {errorMessage && (
          <div className="text-red-500 text-center">{errorMessage}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              First Name
            </label>
            <input
              type="text"
              name="firstname"
              value={formData.firstname}
              onChange={handleChange}
              autoComplete="given-name"
              className={`mt-1 block w-full rounded-md border px-3 py-2 ${
                errors.firstname ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.firstname && (
              <p className="text-red-500 text-xs mt-1">{errors.firstname}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Last Name
            </label>
            <input
              type="text"
              name="lastname"
              value={formData.lastname}
              onChange={handleChange}
              autoComplete="family-name"
              className={`mt-1 block w-full rounded-md border px-3 py-2 ${
                errors.lastname ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.lastname && (
              <p className="text-red-500 text-xs mt-1">{errors.lastname}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
              className={`mt-1 block w-full rounded-md border px-3 py-2 ${
                errors.email ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.email && (
              <p className="text-red-500 text-xs mt-1">{errors.email}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="new-password"
              className={`mt-1 block w-full rounded-md border px-3 py-2 ${
                errors.password ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">{errors.password}</p>
            )}
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-neutral-500 hover:bg-neutral-600 text-white rounded-md"
          >
            Sign Up
          </button>
        </form>

        <div className="flex items-center justify-center mt-4">
          <hr className="w-full border-gray-300" />
          <span className="px-2 text-gray-500">or</span>
          <hr className="w-full border-gray-300" />
        </div>

        <button
          onClick={handleGoogleLogin}
          className="w-full py-2 px-4 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-gray-300 flex items-center justify-center space-x-2 mt-4"
        >
          <FcGoogle className="text-2xl" />
          <span>Continue with Google</span>
        </button>

        <div className="text-center mt-4">
          <a href="/" className="text-sm text-blue-600 hover:text-blue-800">
            Already have an account? Log in
          </a>
        </div>
      </div>
    </div>
  );
};

export default Signup;
