import React, { useState } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useNavigate } from "react-router-dom";  // Importeer useNavigate

const CheckReservering = () => {
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
        "http://localhost:5000/check_numberplate",
        { nummerplaat },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );

      console.log("🔎 API Response Data:", response.data);

      // Controleer of er geen reservering is gevonden
      if (!response.data || response.data.status === 'not_found') {
        // Als er geen reservering is, laat dan de "Geen reservering gevonden" popup zien
        Swal.fire({
          title: "❌ Geen Reservering Gevonden",
          text: "Er is geen reservering gevonden voor deze nummerplaat.",
          icon: "warning",
          showCancelButton: true,
          cancelButtonText: "Sluiten",
          confirmButtonText: "Wilt u reserveren?",
        }).then((result) => {
          if (result.isConfirmed) {
            // Navigeren naar de pagina reserveerd_direct.js met de nummerplaat in de state
            navigate('/reserveerd_direct', { state: { nummerplaat } });
            Swal.fire("Reserveren", "Je wordt doorgestuurd naar het reserveringsformulier.", "info");
          }
        });
        return; // Stop verder verwerken als geen reservering is gevonden
      }

      // Als er een reservering is, toon de details in een popup
      let eindtijd = new Date(response.data.eindtijd);
      let starttijd = new Date(response.data.starttijd);

      // Toon een popup met de eindtijd en locatie
      Swal.fire({
        title: "✅ Reservering Gevonden",
        html: ` 
          <p><strong>📍 Locatie:</strong> ${response.data.locatie}</p>
          <p><strong>⏳ Eindtijd:</strong> ${eindtijd.toLocaleTimeString()}</p>
        `,
        icon: "success",
        confirmButtonText: "OK",
      });

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

export default CheckReservering;
