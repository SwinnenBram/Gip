import React, { useState } from 'react';
import axios from 'axios';
import './style.css'; // Zorg ervoor dat je CSS-bestand goed is geïmporteerd

import { useNavigate } from 'react-router-dom'; // Importeren van useNavigate voor het navigeren

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate(); // Gebruik maken van useNavigate voor redirect

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Verstuur login-verzoek naar backend
      const response = await axios.post('http://localhost:5000/api/login', {
        email: email,
        wachtwoord: password,
      });

      // Als login succesvol is, sla het token op in localStorage
      localStorage.setItem('token', response.data.access_token);

      // Navigeer direct naar het dashboard zonder een pop-up
      navigate('/dashboard'); // Navigeer naar het dashboard na inloggen

    } catch (error) {
      console.error('Er is een fout:', error);
      // Alleen een pop-up bij een fout (bijvoorbeeld ongeldige inloggegevens)
      alert('Ongeldige inloggegevens!'); 
    }
  };

  return (
    <div className="app-container">
      <div className="register-container">
        <h2>Inloggen</h2>
        <form onSubmit={handleSubmit} className="register-form">
          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Wachtwoord"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Inloggen</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
