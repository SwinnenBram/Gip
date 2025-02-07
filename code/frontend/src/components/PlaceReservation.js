import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom"; // Haal de query parameters op
import axios from "axios";

const PlaceReservation = () => {
    const [voertuigen, setVoertuigen] = useState([]);
    const [selectedVoertuig, setSelectedVoertuig] = useState("");
    const [selectedParkeerplaats, setSelectedParkeerplaats] = useState("");
    const [starttijd, setStarttijd] = useState("");
    const [eindtijd, setEindtijd] = useState("");

    // Haal de query parameters op
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const plaatsLocatie = queryParams.get("plaatsLocatie"); // Haal de locatie op
    const datum = queryParams.get("datum"); // Haal de datum op uit de queryparameters

    useEffect(() => {
        fetchVoertuigen();
        if (plaatsLocatie) {
            setSelectedParkeerplaats(plaatsLocatie); // Zet de locatie van de parkeerplaats in de state
        }
        if (datum) {
            // Zet de starttijd op de opgegeven datum met een standaard tijd (bijv. 12:00)
            const defaultStarttijd = `${datum}T12:00`;
            setStarttijd(defaultStarttijd);

            // Zet de eindtijd op 1 uur later dan de starttijd
            const startDate = new Date(defaultStarttijd);
            startDate.setHours(startDate.getHours() + 1); // Voeg 1 uur toe aan de starttijd
            setEindtijd(startDate.toISOString().slice(0, 16)); // Zet de eindtijd op 1 uur later
        }
    }, [plaatsLocatie, datum]);

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

    const handleReservering = async () => {
        const userId = localStorage.getItem('user_id'); 
        if (!userId) {
          alert('Gebruiker is niet ingelogd');
          return;
        }
      
        const reservatieData = {
          gebruiker_id: userId,
          voertuig_id: selectedVoertuig,
          parkeerplaats_id: selectedParkeerplaats,
          starttijd,
          eindtijd,
        };
      
        console.log("Verzonden data:", reservatieData); // Log de data voor debugging
      
        try {
          await axios.post(
            "http://localhost:5000/api/reservaties",
            reservatieData,
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
      
    
    

    // Controleer of de geselecteerde eindtijd minimaal 1 uur na de starttijd ligt
    const handleEindtijdChange = (e) => {
        const newEindtijd = e.target.value;
        const startDate = new Date(starttijd);
        const endDate = new Date(newEindtijd);

        // Als de eindtijd minder dan 1 uur na de starttijd is, stel het opnieuw in
        if (endDate <= startDate) {
            // Voeg 1 uur toe aan de starttijd en stel dat als de eindtijd in
            startDate.setHours(startDate.getHours() + 1);
            setEindtijd(startDate.toISOString().slice(0, 16)); // Update eindtijd
        } else {
            setEindtijd(newEindtijd); // Update eindtijd als het een geldige tijd is
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
                <input 
                    type="text"
                    value={selectedParkeerplaats} // Toon de locatie van de parkeerplaats
                    readOnly
                    className="mb-4 w-full p-2 border rounded bg-gray-100"
                />

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
                    onChange={handleEindtijdChange}  // Gebruik de aangepaste eindtijdlogica
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

export default PlaceReservation;
