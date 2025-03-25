import React, { useState } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useNavigate } from "react-router-dom";  // Importeer useNavigate

const CheckNummerplaat = () => {
  const [nummerplaat, setNummerplaat] = useState(""); // Nummerplaat invoer
  const [loading, setLoading] = useState(false); // Laadstatus
  const navigate = useNavigate();  // Gebruik de navigate functie

  // Functie om nummerplaat op te slaan
  const handleNummerplaatChange = (e) => {
    setNummerplaat(e.target.value);
  };

  // Functie om de reservering op te halen
  const fetchReservering = async () => {
    if (!nummerplaat) {
      Swal.fire("Fout!", "Vul alstublieft een nummerplaat in.", "error");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:5000/check_numberplate_uit",
        { nummerplaat },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );

      console.log("🔎 API Response Data:", response.data);

      // Controleer of er een reservering is gevonden
      if (!response.data || response.data.status === 'not_found') {
        Swal.fire("Fout!", "Geen reservering gevonden voor deze nummerplaat.", "error");
        return;
      }

      // Bereken het bedrag voor betaling
      let starttijd = new Date(response.data.starttijd);
      let eindtijd = new Date();
      let verschil = (eindtijd - starttijd) / 1000 / 60; // Minuten
      let tariefPerMinuut = 5 / 60; // €5 per uur, dus per minuut
      let bedrag = Math.max(60 * tariefPerMinuut, verschil * tariefPerMinuut); // Minimaal 1 uur betalen

      // Toon betalingspagina
      navigate('/betalingspagina', { state: { nummerplaat, bedrag } });
    } catch (error) {
      console.error("⚠️ Fout bij ophalen reservering:", error);
      Swal.fire("Fout", "Er is een fout opgetreden bij het ophalen van de reservering.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <div className="border rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">Controleer Reservering</h2>

        <div className="mt-4">
          <label htmlFor="nummerplaat" className="block">Nummerplaat</label>
          <input
            id="nummerplaat"
            type="text"
            value={nummerplaat}
            onChange={handleNummerplaatChange}
            className="p-2 border rounded w-full"
            placeholder="Voer nummerplaat in"
          />
          <button 
            onClick={fetchReservering} 
            className="mt-4 w-full p-2 bg-blue-500 text-white rounded"
            disabled={loading}
          >
            {loading ? "Bezig..." : "Zoek Reservatie"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CheckNummerplaat;
