import React, { useState } from 'react';
import axios from 'axios';
import './style.css';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(''); // Reset foutmelding bij nieuwe poging
  
    try {
      const response = await axios.post('http://localhost:5000/api/login', {
        email: email,
        wachtwoord: password,
      });
  
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
  
        // Sla de gebruiker ID apart op
        const user = response.data.user;
        if (user) {
          localStorage.setItem('user_id', user.id);  // Zet de user_id apart in localStorage
          localStorage.setItem('user', JSON.stringify(user)); // Sla de volledige user info op
        }
  
        // Navigeren naar dashboard
        navigate('/dashboard');
      } else {
        setErrorMessage('Inloggen mislukt! Geen token ontvangen.');
      }
    } catch (error) {
      console.error('Fout bij inloggen:', error);
  
      if (error.response) {
        if (error.response.status === 401) {
          setErrorMessage('Ongeldige inloggegevens! Probeer het opnieuw.');
        } else {
          setErrorMessage(`Serverfout: ${error.response.data.message || 'Probeer het later opnieuw.'}`);
        }
      } else {
        setErrorMessage('Kan geen verbinding maken met de server.');
      }
    }
  };

  return (
    <div className="app-container">
      <div className="register-container">
        <h2>Inloggen</h2>
        {errorMessage && <p className="error-message">{errorMessage}</p>}
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
