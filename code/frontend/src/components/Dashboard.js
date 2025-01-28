import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './style.css';  // Zorg ervoor dat de CSS-bestand goed is geïmporteerd

const Dashboard = () => {
  const [reservations, setReservations] = useState([]);
  const [userId, setUserId] = useState(1); // Simuleer een ingelogde gebruiker, deze zou normaal uit een token of context komen.

  useEffect(() => {
    const fetchReservations = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/reservaties/${userId}`);
        setReservations(response.data);
      } catch (error) {
        console.error('Er is een fout:', error);
      }
    };

    fetchReservations();
  }, [userId]);

  return (
    <div className="register-container">
      <h2>Dashboard</h2>
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
