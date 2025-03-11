import React, { useState } from "react";
import axios from "axios";
import Swal from "sweetalert2";

const CheckReservering = () => {
  const [nummerplaat, setNummerplaat] = useState(""); // Nummerplaat invoer
  const [loading, setLoading] = useState(false); // Laadstatus

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

      let reserveringen = response.data;
      if (!Array.isArray(reserveringen)) {
        reserveringen = [reserveringen]; // Zorg dat het een array is
      }

      // ✅ Stap 1: Bereken de huidige datum (zonder tijd)
      const vandaag = new Date();
      vandaag.setHours(0, 0, 0, 0);

      // ✅ Stap 2: Filter reserveringen die in de toekomst liggen (vandaag of later)
      let toekomstigeReserveringen = reserveringen.filter((res) => {
        let eindtijd = new Date(res.eindtijd);
        return eindtijd >= vandaag; // Alleen toekomstige of huidige reserveringen
      });

      // ✅ Stap 3: Zoek de eerstvolgende reservering
      let eerstvolgendeReservering = toekomstigeReserveringen.sort((a, b) => 
        new Date(a.eindtijd) - new Date(b.eindtijd)
      )[0];

      console.log("✅ Eerstvolgende reservering:", eerstvolgendeReservering);

      // ✅ Stap 4: Toon de popup ALS er een geldige reservering is
      if (eerstvolgendeReservering) {
        let eindtijd = new Date(eerstvolgendeReservering.eindtijd).toLocaleTimeString();
        Swal.fire({
          title: "✅ Reservering Gevonden",
          html: `
            <p><strong>📍 Locatie:</strong> ${eerstvolgendeReservering.locatie}</p>
            <p><strong>⏳ Eindtijd:</strong> ${eindtijd}</p>
          `,
          icon: "success",
          confirmButtonText: "OK",
        });
      } else {
        console.log("❌ Geen toekomstige reservering gevonden!");
        Swal.fire("Geen reservering", "Er is geen toekomstige reservering gevonden voor deze nummerplaat.", "warning");
      }
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
