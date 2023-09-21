import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const axiosBaseURL = axios.create({
  baseURL: "http://127.0.0.1:5000",
});

function App() {
  // React States
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (event) => {
    //Prevent page reload
    event.preventDefault();
    console.log(username, password);

    axiosBaseURL
      .get("/api/login", {
        auth: {
          username: username,
          password: password,
        },
      })
      .then((response) => {
        console.log(response.data);
        setToken(response.data.token);
        setIsSubmitted(true);
      })
      .catch((error) => {
        console.log(error);
        alert("Incorrect credentials")
      });
  };

  const renderForm = (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
  return (
    <div className="app">
      <div className="login-form">
        <div className="title">Sign In</div>
        {isSubmitted ? <div>User is successfully logged in</div> : renderForm}
      </div>
    </div>
  );
}

export default App;
