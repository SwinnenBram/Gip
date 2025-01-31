import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './style.css'; // Zorg ervoor dat de CSS-bestand goed is geïmporteerd

const Dashboard = () => {
  const [reservations, setReservations] = useState([]);
  const [welcomeMessage, setWelcomeMessage] = useState('');
  const [userId, setUserId] = useState(1); // Simuleer een ingelogde gebruiker, deze zou normaal uit een token of context komen.

  useEffect(() => {
    // Haal eerst de welkomstboodschap op
    const fetchWelcomeMessage = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/dashboard', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}` // Voeg het token toe aan de headers voor authenticatie
          }
        });
        setWelcomeMessage(response.data.message);
      } catch (error) {
        console.error('Er is een fout met het ophalen van het welkomstbericht:', error);
      }
    };

    // Haal reserveringen op
    const fetchReservations = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/reservaties`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setReservations(response.data);
      } catch (error) {
        console.error('Er is een fout:', error);
      }
    };

    fetchWelcomeMessage(); // Haal welkomstbericht op
    fetchReservations(); // Haal reserveringen op
  }, [userId]);

  return (
    <div className="register-container">
      <h2>Dashboard</h2>
      <h3>{welcomeMessage}</h3> {/* Toon het welkomstbericht */}
      <h3>Reserveringen</h3>
      <ul>
        {reservations.length > 0 ? (
          reservations.map((reservation) => (
            <li key={reservation.reservatienummer}>
              {reservation.reservatienummer} - Van {reservation.starttijd} tot {reservation.eindtijd}
            </li>
          ))
        ) : (
          <li>Geen reserveringen gevonden.</li>
        )}
      </ul>
    </div>
  );
};

export default Dashboard;
