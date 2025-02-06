import React, { useEffect, useState } from "react";
import axios from "axios";

const Reservation = () => {
  const [voertuigen, setVoertuigen] = useState([]);
  const [parkeerplaatsen, setParkeerplaatsen] = useState([]);
  const [selectedVoertuig, setSelectedVoertuig] = useState("");
  const [selectedParkeerplaats, setSelectedParkeerplaats] = useState("");
  const [starttijd, setStarttijd] = useState("");
  const [eindtijd, setEindtijd] = useState("");

  useEffect(() => {
    fetchVoertuigen();
    fetchParkeerplaatsen();
  }, []);

  const fetchVoertuigen = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/voertuigenzoeken", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      setVoertuigen(response.data);
    } catch (error) {
      console.error("Fout bij ophalen voertuigen:", error);
    }
  };

  const fetchParkeerplaatsen = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/parkeerplaatsen");
      setParkeerplaatsen(response.data);
    } catch (error) {
      console.error("Fout bij ophalen parkeerplaatsen:", error);
    }
  };

  const handleReservering = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5000/api/reservaties",
        {
          gebruiker_id: localStorage.getItem("user_id"),
          voertuig_id: selectedVoertuig,
          parkeerplaats_id: selectedParkeerplaats,
          starttijd,
          eindtijd,
        },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }
      );
      alert("Reservering succesvol aangemaakt!");
    } catch (error) {
      alert("Fout bij reservering.");
      console.error("Fout bij reserveren:", error);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <div className="border rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">Maak een Reservering</h2>
        
        <label>Voertuig</label>
        <select onChange={(e) => setSelectedVoertuig(e.target.value)} className="mb-4 w-full p-2 border rounded">
          <option value="">Selecteer een voertuig</option>
          {voertuigen.map((v) => (
            <option key={v.nummerplaat} value={v.id}>{v.nummerplaat}</option>
          ))}
        </select>

        <label>Parkeerplaats</label>
        <select onChange={(e) => setSelectedParkeerplaats(e.target.value)} className="mb-4 w-full p-2 border rounded">
          <option value="">Selecteer een parkeerplaats</option>
          {parkeerplaatsen.map((p) => (
            <option key={p.id} value={p.id}>{p.locatie} - {p.grootte}</option>
          ))}
        </select>

        <label>Starttijd</label>
        <input 
          type="datetime-local" 
          value={starttijd} 
          onChange={(e) => setStarttijd(e.target.value)} 
          className="mb-4 w-full p-2 border rounded"
        />

        <label>Eindtijd</label>
        <input 
          type="datetime-local" 
          value={eindtijd} 
          onChange={(e) => setEindtijd(e.target.value)} 
          className="mb-4 w-full p-2 border rounded"
        />

        <button 
          className="mt-4 w-full p-2 bg-blue-500 text-white rounded" 
          onClick={handleReservering}
        >
          Reserveren
        </button>
      </div>
    </div>
  );
};

export default Reservation;
