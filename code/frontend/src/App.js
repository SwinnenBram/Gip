import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './components/style.css';

import Header from './components/Header';
import Register from './components/Register';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import VehicleManagement from './components/VehicleManagement';  // Importeer de nieuwe pagina

// 🔹 ProtectedRoute: Zorgt dat alleen ingelogde gebruikers de pagina's zien
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token'); // Haal het token op uit localStorage
  console.log('Token gevonden in ProtectedRoute:', token);  // Toegevoegd voor debugging

  if (!token) {
    console.log('Geen token, doorsturen naar login');
    return <Navigate to="/login" />;  // Als er geen token is, stuur naar login
  }

  return children;  // Als token bestaat, toon de beschermde route
};

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('Token bij App.js load:', token);  // Toegevoegd voor debugging

    if (token) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  if (isAuthenticated === null) {
    return <p>Loading...</p>;  // Wacht totdat de loginstatus is geladen
  }

  return (
    <Router>
      <Header /> {/* ✅ De navigatiebalk blijft altijd zichtbaar */}
      <div className="container">
        <Routes>
          {/* Publieke routes */}
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<h1>Welcome to the Smart Parking Garage!</h1>} />

          {/* Beveiligde routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/vehicle-management"  // ✅ Nieuwe route voor VehicleManagement toegevoegd
            element={
              <ProtectedRoute>
                <VehicleManagement />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
