import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css'; // Zorg ervoor dat deze CSS-bestand goed is geïmporteerd

const Header = () => {
  // Controleer of de gebruiker ingelogd is (d.w.z. of er een token aanwezig is)
  const token = localStorage.getItem('token');
  const navigate = useNavigate();  // Voor navigeren naar de loginpagina na uitloggen
  
  const handleLogout = () => {
    // Verwijder de token uit localStorage en stuur de gebruiker naar de loginpagina
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">Smart Parking</Link>
        <ul className="navbar-menu">
          {/* Altijd tonen: Register en Login */}
          {!token && (
            <>
              <li className="navbar-item">
                <Link to="/register" className="navbar-link">Register</Link>
              </li>
              <li className="navbar-item">
                <Link to="/login" className="navbar-link">Login</Link>
              </li>
            </>
          )}

          {/* Alleen tonen als de gebruiker ingelogd is */}
          {token && (
            <>
              <li className="navbar-item">
                <Link to="/dashboard" className="navbar-link">Dashboard</Link>
              </li>
              <li className="navbar-item">
                <Link to="/vehicle-management" className="navbar-link">Voertuigen</Link> {/* Link toegevoegd */}
              </li>
              <li className="navbar-item">
                <Link to="/reservation" className="navbar-link">Reservering</Link> {/* Link naar Reservation toegevoegd */}
              </li>
              <li className="navbar-item">
                <Link to="/nummerplaat" className="navbar-link">In</Link> {/* Link naar Reservation toegevoegd */}
              </li>
              <li className="navbar-item">
                <Link to="/checknummerplaat" className="navbar-link">Uit</Link> {/* Link naar Reservation toegevoegd */}
              </li>
              <li className="navbar-item">
                <Link to="/AdminDashboard" className="navbar-link">Admin</Link> {/* Link naar nummerplaat toegevoegd */}
              </li>
              {/* Uitlogknop (pictogram of tekst) */}
              <li className="navbar-item">
                <button onClick={handleLogout} className="navbar-link logout-btn">Uitloggen</button>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Header;