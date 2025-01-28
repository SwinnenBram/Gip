import React, { useState } from 'react';
import axios from 'axios';
import './style.css';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/api/register', {
        naam: name,
        email: email,
        telefoonnummer: phone,
        wachtwoord: password,
      });
      alert(response.data.message); // Succesbericht
    } catch (error) {
      console.error('Er is een fout:', error);
      alert('Er is iets mis gegaan bij het registreren!');
    }
  };

  return (
    <div className="app-container">
      <div className="register-container">
        <h2>Registreren</h2>
        <form onSubmit={handleSubmit} className="register-form">
          <input
            type="text"
            placeholder="Naam"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="tel"
            placeholder="Telefoonnummer"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
          <input
            type="password"
            placeholder="Wachtwoord"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Registreer</button>
        </form>
      </div>
    </div>
  );
};

export default Register;
