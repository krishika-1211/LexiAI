import React from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import Signup from "./pages/signup";
import Login from "./pages/login";
import Sidebar from "./pages/Sidebar";
import Topic from "./pages/Topic";
import Forgate from "./password/Forgate";
import Cookies from "js-cookie";
import Billing from "./pages/Billing";
import History from "./pages/History";
import GoogleAuthCallback from "./pages/GoogleAuthCallback";
import CommunicationPage from "./pages/CommunicationPage";


const PrivateRoute = ({ element: Component, ...rest }) => {
  const token = Cookies.get("token");
  return token ? <Component {...rest} /> : <Navigate to="/" />;
};

const AppContent = () => {
  const location = useLocation();
  const hideSidebarPaths = ["/", "/signup", "/forgate-password"];

  return (
    <>
      {!hideSidebarPaths.includes(location.pathname) && <Sidebar />}
      <div className={!hideSidebarPaths.includes(location.pathname) ? "md:ml-64" : ""}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/home" element={<PrivateRoute element={Home} />} />
          <Route path="/topic" element={<PrivateRoute element={Topic} />} />
          <Route path="/forgate-password" element={<Forgate />} />
          <Route path="/billing" element={<PrivateRoute element={Billing} />} />
          <Route path="/history" element={<PrivateRoute element={History} />} />
          <Route path="/auth/callback" element={<GoogleAuthCallback />} />
          <Route path="/chat" element={<CommunicationPage />} />
        </Routes>
      </div>
    </>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
