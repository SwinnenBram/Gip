import React from "react";
import { useNavigate } from "react-router-dom";

export default function Reservation() {
  const navigate = useNavigate(); // 🚀 Gebruik de navigatie-hook

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-xl shadow-md space-y-4">
      <h1 className="text-xl font-bold">Reservatie Pagina</h1>
      <p className="text-gray-600">Kies je verdieping:</p>
      
      <div className="flex space-x-4">
        <button 
          onClick={() => navigate("/verdiep-1")}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-700"
        >
          Verdiep -1
        </button>
        
        <button 
          onClick={() => navigate("/verdiep-2")}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-700"
        >
          Verdiep -2
        </button>
      </div>
    </div>
  );
}
