import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import SignupPage from "./Pages/SignupPage";
import ForgotPassword from "./Pages/ForgotPasswordPage/ForgotPasswordPage";
import ChangePassword from  "./Pages/ChangePassword"
import HomePage from "./Pages/HomePage";
import axios from "axios"
import AdminDashboard from "./Pages/AdminDashboard";
import LoggedIn from './components/LoggedIn'

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';


axios.defaults.baseURL = process.env.REACT_APP_BASE_URL;

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/loggedin" element={<LoggedIn />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path = "/resetpassword" element = {<ChangePassword />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
