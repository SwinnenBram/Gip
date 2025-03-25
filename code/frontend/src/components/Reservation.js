import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Reservation() {
  const [selectedDate, setSelectedDate] = useState(""); // Bewaar de geselecteerde datum
  const [minDate, setMinDate] = useState(""); // Minimum datum (minstens één dag verder)
  const navigate = useNavigate(); // 🚀 Gebruik de navigatie-hook

  // Functie om de datum bij te werken
  const handleDateChange = (event) => {
    setSelectedDate(event.target.value);
  };

  // Stel de minimum datum in bij het laden van de component
  useEffect(() => {
    const today = new Date();
    today.setDate(today.getDate() + 1); // Voeg 1 dag toe aan de huidige datum
    const formattedDate = today.toISOString().split("T")[0]; // Zet het in het juiste formaat (YYYY-MM-DD)
    setMinDate(formattedDate); // Stel de minimum datum in
  }, []);

  // Functie om door te gaan naar de verdieping, waarbij de geselecteerde datum wordt doorgestuurd
  const goToFloor = (floor) => {
    if (!selectedDate) {
      alert("Selecteer eerst een datum.");
      return;
    }
    
    const selectedDateObj = new Date(selectedDate);
    const minDateObj = new Date(minDate);

    // Controleer of de geselecteerde datum minstens één dag in de toekomst is
    if (selectedDateObj < minDateObj) {
      alert("Je kunt niet reserveren voor de dag van vandaag of het verleden. Kies een datum minimaal één dag verder.");
      return;
    }

    // Navigeren naar de verdieping, met de datum in de queryparameter
    navigate(`/verdiep-${floor}?datum=${selectedDate}`);
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-xl shadow-md space-y-4">
      <h1 className="text-xl font-bold">Reservatie Pagina</h1>
      <p className="text-gray-600">Kies een datum:</p>
      
      {/* Datuminvoer */}
      <div>
        <label htmlFor="date" className="block text-gray-600">Kies een datum:</label>
        <input
          type="date"
          id="date"
          value={selectedDate}
          onChange={handleDateChange}
          className="px-4 py-2 border rounded-md"
          min={minDate} // Voorkom dat de gebruiker een datum selecteert die vóór de minimumdatum ligt
        />
      </div>

      <div className="flex space-x-4 mt-4">
        <button 
          onClick={() => goToFloor(1)} // Navigeren naar verdieping 1
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-700"
        >
          Verdiep -1
        </button>
        
        <button 
          onClick={() => goToFloor(2)} // Navigeren naar verdieping 2
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-700"
        >
          Verdiep -2
        </button>
      </div>
    </div>
  );
}
