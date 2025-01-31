import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const VehicleManagement = () => {
  const [voertuigen, setVoertuigen] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newVoertuig, setNewVoertuig] = useState({
    nummerplaat: '',
    grootte: '',  // Dit wordt nu een string die een van de drie opties kan zijn
    is_elektrisch: false,
    heeft_handicapkaart: false
  });
  const navigate = useNavigate();

  useEffect(() => {
    const fetchVoertuigen = async () => {
      const token = localStorage.getItem('token');  // Haal de token op uit localStorage

      try {
        const response = await axios.get('http://localhost:5000/api/voertuigen', {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}` // Voeg het token toe aan de headers voor authenticatie
            }
          });
        setVoertuigen(response.data);  // Zet de voertuigen in de state
        setLoading(false);  // Zet de laadtoestand uit
      } catch (error) {
        console.error('Fout bij het ophalen van voertuigen:', error);
        setLoading(false);  // Zet de laadtoestand uit, zelfs als er een fout is
        alert('Er is een probleem met het ophalen van de voertuigen. Probeer het later opnieuw.');
        navigate('/login');
      }
    };

    fetchVoertuigen();
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewVoertuig({
      ...newVoertuig,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');  // Haal de token op uit localStorage
    if (!token) {
      navigate('/login');  // Als er geen token is, stuur de gebruiker naar de loginpagina
      return;
    }

    try {
      // Stuur een POST-aanroep naar de backend om het voertuig toe te voegen
      const response = await axios.post('http://localhost:5000/api/voertuigen', newVoertuig, {
        headers: {
          Authorization: `Bearer ${token}`  // Voeg de JWT-token toe aan de headers
        }
      });

      alert(response.data.message);  // Toon een bericht als het voertuig succesvol is toegevoegd

      // Voeg het nieuwe voertuig toe aan de lijst zonder de pagina opnieuw te laden
      setVoertuigen((prevVoertuigen) => [...prevVoertuigen, newVoertuig]);
      setNewVoertuig({
        nummerplaat: '',
        grootte: '',  // Reset de grootte naar een lege waarde
        is_elektrisch: false,
        heeft_handicapkaart: false
      });  // Reset het formulier

    } catch (error) {
      console.error('Fout bij het toevoegen van het voertuig:', error);
      alert('Er is een probleem met het toevoegen van het voertuig. Probeer het later opnieuw.');
    }
  };

  return (
    <div className="container">
      <h1>Mijn Voertuigen</h1>

      {loading ? (
        <p>Loading...</p>  // Toon een laadbericht
      ) : (
        <>
          {voertuigen.length > 0 ? (
            <ul>
              {voertuigen.map((voertuig, index) => (
                <li key={index}>
                  <p><strong>Nummerplaat:</strong> {voertuig.nummerplaat}</p>
                  <p><strong>Grootte:</strong> {voertuig.grootte}</p>
                  <p><strong>Elektrisch:</strong> {voertuig.is_elektrisch ? 'Ja' : 'Nee'}</p>
                  <p><strong>Handicapkaart:</strong> {voertuig.heeft_handicapkaart ? 'Ja' : 'Nee'}</p>
                  <hr />
                </li>
              ))}
            </ul>
          ) : (
            <p>Je hebt geen voertuigen geregistreerd.</p>
          )}
        </>
      )}

      <h2>Voertuig Toevoegen</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Nummerplaat:
          <input
            type="text"
            name="nummerplaat"
            value={newVoertuig.nummerplaat}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Grootte:
          <select
            name="grootte"
            value={newVoertuig.grootte}
            onChange={handleChange}
            required
          >
            <option value="">Kies een grootte</option>
            <option value="Klein">Klein</option>
            <option value="Medium">Medium</option>
            <option value="Groot">Groot</option>
          </select>
        </label>
        <label>
          Elektrisch:
          <input
            type="checkbox"
            name="is_elektrisch"
            checked={newVoertuig.is_elektrisch}
            onChange={handleChange}
          />
        </label>
        <label>
          Handicapkaart:
          <input
            type="checkbox"
            name="heeft_handicapkaart"
            checked={newVoertuig.heeft_handicapkaart}
            onChange={handleChange}
          />
        </label>
        <button type="submit">Voertuig Toevoegen</button>
      </form>
    </div>
  );
};

export default VehicleManagement;
