// src/components/PrivateRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token'); // Neem de token uit de localStorage

  // Als er geen token is, stuur de gebruiker naar de login-pagina
  if (!token) {
    return <Navigate to="/login" />;
  }

  // Als er wel een token is, render de kinderen van de route
  return children;
};

export default PrivateRoute;
