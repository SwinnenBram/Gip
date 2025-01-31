import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './style.css';
import Header from './Header'; // Zorg ervoor dat de header aanwezig is

const Vehicle = () => {
  const [nummerplaat, setNummerplaat] = useState('');
  const [grootte, setGrootte] = useState('klein');
  const [isElektrisch, setIsElektrisch] = useState(false);
  const [heeftHandicapkaart, setHeeftHandicapkaart] = useState(false);
  const [gebruiker, setGebruiker] = useState(null);
  const [welkomBericht, setWelkomBericht] = useState(''); // Nieuw state voor het welkomstbericht
  const [voertuigen, setVoertuigen] = useState([]);
  const navigate = useNavigate();

  // Haal gebruiker en voertuigen op bij het laden van de component
  useEffect(() => {
    const fetchGebruiker = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Je moet ingelogd zijn om voertuigen te bekijken of toe te voegen.');
        return;
      }

      try {
        // Haal gebruiker op via de API
        const response = await axios.get('/api/user', {
          headers: { Authorization: `Bearer ${token}` },
        });

        setGebruiker(response.data); // Sla de gebruiker op
        fetchVoertuigen(response.data.id); // Haal voertuigen van de gebruiker op
        fetchWelkomBericht(response.data); // Haal het welkomstbericht op
      } catch (error) {
        console.error('Fout bij het ophalen van gebruiker:', error);
        localStorage.removeItem('token'); // Verwijder ongeldig token
        alert('Er is een probleem met je sessie, log opnieuw in.');
        navigate('/login'); // Stuur naar de login pagina als het ophalen van de gebruiker faalt
      }
    };

    fetchGebruiker();
  }, [navigate]);

  // Haal voertuigen op op basis van het gebruiker ID
  const fetchVoertuigen = async (gebruikerId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/voertuigen/${gebruikerId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setVoertuigen(response.data);
    } catch (error) {
      console.error('Fout bij het ophalen van voertuigen:', error);
      alert('Kon de voertuigen niet ophalen, probeer het later opnieuw.');
    }
  };

  // Haal welkomstbericht op
  const fetchWelkomBericht = async (gebruikerData) => {
    try {
      const message = `Hey ${gebruikerData.naam}, met email ${gebruikerData.email}, welkom dat je er bent!`;
      setWelkomBericht(message);
    } catch (error) {
      console.error('Fout bij het ophalen van welkomstbericht:', error);
      alert('Er is een probleem met het ophalen van het welkomstbericht.');
    }
  };

  // Voeg een nieuw voertuig toe
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!gebruiker) {
      alert('Je moet ingelogd zijn om een voertuig toe te voegen.');
      return;
    }

    const voertuigData = {
      nummerplaat,
      grootte,
      is_elektrisch: isElektrisch,
      heeft_handicapkaart: heeftHandicapkaart,
      gebruiker_id: gebruiker.id,
    };

    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/voertuigen', voertuigData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      alert('Voertuig succesvol toegevoegd!');
      setNummerplaat('');
      setGrootte('klein');
      setIsElektrisch(false);
      setHeeftHandicapkaart(false);
      fetchVoertuigen(gebruiker.id); // 🚀 Vernieuw de voertuiglijst
    } catch (error) {
      console.error('Fout bij het toevoegen van voertuig:', error);
      alert('Er is iets misgegaan. Probeer opnieuw.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4">Voertuigbeheer</h1>

        {/* 🔹 Welkomstbericht */}
        {gebruiker ? (
          <p className="mb-4">{welkomBericht}</p> // Welkomstbericht tonen
        ) : (
          <p className="mb-4">Je bent niet ingelogd. Log in om voertuigen toe te voegen of te bekijken.</p>
        )}

        {/* 🔹 Formulier voor voertuig toevoegen */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-medium">Nummerplaat</label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded p-2"
              value={nummerplaat}
              onChange={(e) => setNummerplaat(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block font-medium">Grootte</label>
            <select
              className="w-full border border-gray-300 rounded p-2"
              value={grootte}
              onChange={(e) => setGrootte(e.target.value)}
            >
              <option value="klein">Klein</option>
              <option value="medium">Medium</option>
              <option value="groot">Groot</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={isElektrisch}
              onChange={(e) => setIsElektrisch(e.target.checked)}
            />
            <label>Elektrisch</label>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={heeftHandicapkaart}
              onChange={(e) => setHeeftHandicapkaart(e.target.checked)}
            />
            <label>Handicapkaart</label>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Voertuig Toevoegen
          </button>
        </form>

        <div className="mt-6">
          <h2 className="text-xl font-bold mb-4">Mijn Voertuigen</h2>
          {voertuigen.length > 0 ? (
            <ul className="space-y-2">
              {voertuigen.map((voertuig, index) => (
                <li
                  key={index}
                  className="border border-gray-300 rounded p-4 flex justify-between items-center"
                >
                  <span>{voertuig.nummerplaat} ({voertuig.grootte})</span>
                  <span>
                    {voertuig.is_elektrisch && 'Elektrisch'}
                    {voertuig.heeft_handicapkaart && ' | Handicapkaart'}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p>Geen voertuigen gevonden.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Vehicle;
