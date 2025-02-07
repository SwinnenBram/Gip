import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Reservation() {
  const [selectedDate, setSelectedDate] = useState(""); // Bewaar de geselecteerde datum
  const navigate = useNavigate(); // 🚀 Gebruik de navigatie-hook

  // Functie om de datum bij te werken
  const handleDateChange = (event) => {
    setSelectedDate(event.target.value);
  };

  // Functie om door te gaan naar de verdieping, waarbij de geselecteerde datum wordt doorgestuurd
  const goToFloor = (floor) => {
    if (!selectedDate) {
      alert("Selecteer eerst een datum.");
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
