import React, { useState } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useLocation, useNavigate } from "react-router-dom";  // Importeer useLocation en useNavigate

const Betalingspagina = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { nummerplaat, bedrag } = location.state;  // Verkrijg nummerplaat en bedrag van de vorige pagina
  const [betalingsStatus, setBetalingsStatus] = useState(false);  // Betalingsstatus

  // Simuleer betaling
  const verwerkBetaling = async () => {
    try {
      // Simuleer het betalingsproces
      Swal.fire({
        title: "Betaling Bezig...",
        text: "Uw betaling wordt verwerkt.",
        icon: "info",
        showConfirmButton: false,
        allowOutsideClick: false,
        willOpen: () => {
          Swal.showLoading();
        }
      });

      // Stel hier een echte betalingsverwerking in indien nodig.
      await new Promise(resolve => setTimeout(resolve, 2000));  // Simuleer vertraging van 2 seconden

      Swal.close();  // Sluit de laadbalk

      // Verwijder de reservering uit de database na betaling
      const response = await axios.post(
        "http://localhost:5000/verwijder_reservering",
        { nummerplaat },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );

      // Toon bevestiging
      Swal.fire("Betaling Geslaagd", `Betaling van €${bedrag.toFixed(2)} is succesvol ontvangen.`, "success");
      setBetalingsStatus(true);

      // Verwijder de reservering en leid gebruiker naar de startpagina
      setTimeout(() => navigate("/"), 2000);

    } catch (error) {
      console.error("⚠️ Betaling fout:", error);
      Swal.fire("Fout", "Er is een fout opgetreden bij het verwerken van de betaling.", "error");
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <div className="border rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">Betaling voor Nummerplaat: {nummerplaat}</h2>
        <p className="mb-4">Te betalen bedrag: €{bedrag.toFixed(2)}</p>

        <button
          onClick={verwerkBetaling}
          className="w-full p-2 bg-green-500 text-white rounded"
          disabled={betalingsStatus}
        >
          {betalingsStatus ? "Betaling Voltooid" : "Betalen"}
        </button>
      </div>
    </div>
  );
};

export default Betalingspagina;
