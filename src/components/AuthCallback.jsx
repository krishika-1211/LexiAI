// import React, { useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import Cookies from "js-cookie";

// const AuthCallback = () => {
//   const navigate = useNavigate();

//   useEffect(() => {
//     const urlParams = new URLSearchParams(window.location.search);
//     const token = urlParams.get("token");

//     if (token) {
//       Cookies.set("token", token, { expires: 7 }); // Store token for 7 days
//       navigate("/home"); // Redirect to home
//     } else {
//       navigate("/login");
//     }
//   }, [navigate]);

//   return <p>Authenticating...</p>;
// };

// export default AuthCallback;
