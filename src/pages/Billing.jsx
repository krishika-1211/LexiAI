import React, { useState } from "react";
import Cookies from "js-cookie";
// import { jwtDecode } from "jwt-decode";

const Billing = () => {
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  const [currentPlan, setCurrentPlan] = useState("Free");
  const [selectedPlan, setSelectedPlan] = useState("");
  const totalCredits = 10000;
  const usedCredits = 0;

  


  const handleContinue = () => {
    const token = Cookies.get("token");
    fetch(`${API_BASE_URL}/checkout-session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ plan_name: selectedPlan }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        } else {
          alert("Failed to create checkout session");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-neutral-100 text-black p-6">
      <div className="w-full max-w-6xl bg-neutral-300 shadow-md rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4">Subscription</h1>
        {/* Subscription Details */}
        <div className="bg-neutral-200 p-4 rounded-lg border border-gray-600">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">Subscription Details</h2>
            <button className="px-4 py-2 bg-neutral-400 rounded-md text-sm">
              Manage billing info
            </button>
          </div>
          <div className="mt-4 border-t border-gray-600 pt-4">
            <div className="flex justify-between items-center">
              <span className="text-black">Current Plan</span>
              <span className="px-3 py-1 bg-neutral-400 rounded-md text-sm">
                {currentPlan}
              </span>
            </div>
          </div>
          {/* Credit Usage */}
          {/* <div className="mt-4 border-t border-gray-600 pt-4">
            <span className="text-gray-300">Credit Usage</span>
            <div className="w-full bg-gray-600 h-2 rounded-full mt-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${(usedCredits / totalCredits) * 100}%` }}
              ></div>
            </div>
            <p className="text-gray-400 text-sm mt-2">
              {usedCredits}/{totalCredits} used (Resets in 24 days)
            </p>
          </div> */}
        </div>
      </div>
      {/* Plan Selection */}
      <div className="w-full max-w-6xl bg-neutral-300 shadow-md rounded-lg p-6 mt-3">
        <div className="bg-neutral-200 p-4 rounded-lg border border-gray-600 mb-4">
          <h2 className="text-lg font-semibold">Select a Plan</h2>
          <div className="mt-4 flex gap-4">
            <div
              className={`border rounded-lg p-4 w-1/2 cursor-pointer ${
                selectedPlan === "Basic" ? "border-gray-600" : "border-neutral-400"
              }`}
              onClick={() => setSelectedPlan("Basic")}
            >
              <h3 className="text-xl font-semibold">Basic Plan</h3>
              <ul className="text-sm text-black mt-2 list-disc list-inside">
  <li>Limited conversation sessions per month.</li>
  <li>Basic speech recognition.</li>
  <li>Simple AI feedback.</li>
</ul>
              <p className="text-lg font-bold mt-2">$5/month</p>
            </div>
            <div
              className={`border rounded-lg p-4 w-1/2 cursor-pointer ${
                selectedPlan === "Standard"
                  ?  "border-gray-600" : "border-neutral-400"
              }`}
              onClick={() => setSelectedPlan("Standard")}
            >
              <h3 className="text-xl font-semibold">Standard Plan</h3>
              <ul className="text-sm text-black mt-2 list-disc list-inside">
  <li>Limited conversation sessions per month.</li>
  <li>Basic speech recognition.</li>
  <li>Simple AI feedback.</li>
</ul>

              <p className="text-lg font-bold mt-2">$10/month</p>
            </div>
          </div>
        </div>
        <button
          className="px-4 py-2 bg-neutral-500 text-white rounded-md"
          onClick={handleContinue}
          disabled={!selectedPlan}
        >
          Continue to {selectedPlan}
        </button>
      </div>
    </div>
  );
};

export default Billing;
