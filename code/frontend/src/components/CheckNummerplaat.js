import React, { useState } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useNavigate } from "react-router-dom";

const CheckNummerplaat = () => {
  const [nummerplaat, setNummerplaat] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleNummerplaatChange = (e) => {
    setNummerplaat(e.target.value);
  };

  const berekenPrijs = (minuten) => {
    const uur = minuten / 60;
    if (uur <= 1) return 5; 
    if (uur <= 3) return 5 + (uur - 1) * 5;
    if (uur <= 6) return 5 + 2 * 5 + (uur - 3) * 4;
    return Math.min(20, 5 + 2 * 5 + 3 * 4 + (uur - 6) * 3);
  };

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

      if (!response.data || response.data.status === "not_found") {
        Swal.fire("Fout!", "Geen reservering gevonden voor deze nummerplaat.", "error");
        return;
      }

      let starttijd = new Date(response.data.starttijd);
      let eindtijd = new Date();
      let verschil = (eindtijd - starttijd) / 1000 / 60;
      let bedrag = berekenPrijs(verschil);

      navigate("/betalingspagina", { state: { nummerplaat, bedrag } });
    } catch (error) {
      console.error("Fout bij ophalen reservering:", error);
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
