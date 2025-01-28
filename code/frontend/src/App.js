import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './components/style.css'; 

import Header from './components/Header';
import Register from './components/Register';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

const App = () => {
  return (
    <Router>
      <div>
        <Header /> {/* De Header component bevat de navigatiebalk */}
        <div className="container">
          <Routes>
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/" element={<h1>Welcome to the Smart Parking Garage!</h1>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
