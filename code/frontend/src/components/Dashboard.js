import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './style.css';

const Dashboard = () => {
  const [reservations, setReservations] = useState([]);
  const [welcomeMessage, setWelcomeMessage] = useState('');
  const [userId, setUserId] = useState(1); // Simuleer een ingelogde gebruiker

  useEffect(() => {
    // Haal eerst de welkomstboodschap op
    const fetchWelcomeMessage = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/dashboard', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
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
        const response = await axios.get('http://localhost:5000/api/reservaties', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setReservations(response.data);
      } catch (error) {
        console.error('Er is een fout:', error);
      }
    };

    fetchWelcomeMessage();
    fetchReservations();
  }, [userId]);

  // Verwijder een reservering
  const deleteReservation = async (reservatienummer) => {
    try {
      const response = await axios.delete(`http://localhost:5000/api/reservaties/${reservatienummer}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      alert(response.data.message); // Toon bevestigingsbericht
      setReservations(reservations.filter((reservation) => reservation.reservatienummer !== reservatienummer)); // Verwijder de reservering uit de staat
    } catch (error) {
      console.error('Er is een fout bij het verwijderen van de reservering:', error);
      alert('Er is iets mis gegaan bij het verwijderen van de reservering');
    }
  };

  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      <h3>{welcomeMessage}</h3>
      <h3>Reserveringen</h3>

      {/* Tabel voor het weergeven van reserveringen */}
      <table className="reservations-table">
        <thead>
          <tr>
            <th>Reserveringsnummer</th>
            <th>Van</th>
            <th>Tot</th>
            <th>Parkeerplaats</th>
            <th>Acties</th> {/* Kolom voor de verwijderknop */}
          </tr>
        </thead>
        <tbody>
          {reservations.length > 0 ? (
            reservations.map((reservation) => (
              <tr key={reservation.reservatienummer}>
                <td>{reservation.reservatienummer}</td>
                <td>{reservation.starttijd}</td>
                <td>{reservation.eindtijd}</td>
                <td>{reservation.parkeerplaats_locatie}</td>
                <td>
                  <button onClick={() => deleteReservation(reservation.reservatienummer)} className="delete-btn">
                    Verwijder
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5">Geen actieve reserveringen gevonden.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
