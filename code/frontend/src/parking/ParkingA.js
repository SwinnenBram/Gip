import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./Parkeerplaatsen.css";

const ParkeerplaatsenA = () => {
    const [parkeerplaatsen, setParkeerplaatsen] = useState([]);
    const [loading, setLoading] = useState(true); // Laadstatus
    const [error, setError] = useState(null); // Foutmelding opslaan
    const navigate = useNavigate();
    const location = useLocation();

    // Haal de datum op uit de queryparameter
    const urlParams = new URLSearchParams(location.search);
    const datum = urlParams.get("datum"); 

    useEffect(() => {
        if (datum) {
            setLoading(true);
            setError(null); // Reset fouten bij nieuwe aanvraag
    
            // Haal het token uit localStorage (of waar het ook opgeslagen is)
            const token = localStorage.getItem("token");
    
            // 🚗 **Stap 1: Haal parkeerplaatsen op**
            axios.get(`http://localhost:5000/api/parkings?datum=${datum}&zone=A`, {
                headers: {
                    Authorization: `Bearer ${token}` // Voeg token toe aan de header
                }
            })
                .then((response) => {
                    setParkeerplaatsen(response.data);
    
                    // Log de volledige reserveringen
                    const gereserveerdePlekken = response.data.filter(plek => plek.gereserveerd);
                    console.log(`Gereserveerde parkeerplaatsen op ${datum}:`, gereserveerdePlekken);
    
                    // Als je de volledige details van de reserveringen wilt zien:
                    gereserveerdePlekken.forEach(plek => {
                        console.log(`Reservering details voor ${plek.locatie}:`);
                        console.log(`Reservering ID: ${plek.reservatie_id}`);
                        console.log(`Starttijd: ${plek.starttijd}`);
                        console.log(`Eindtijd: ${plek.eindtijd}`);
                        console.log(`Klant: ${plek.klant}`);
                    });
                })
                .catch((error) => {
                    console.error("❌ Fout bij het ophalen van parkeerplaatsen:", error);
                    setError("Kan parkeerplaatsen niet laden.");
                })
                .finally(() => {
                    setLoading(false);
                });
        }
    }, [datum]);
    
    

    const handleClick = (locatie) => {
        navigate(`/place-reservation?plaatsLocatie=${locatie}&datum=${datum}`);
    };

    return (
        <div className="container">
            <h1 className="title">Parkeerplaatsen - Zone A</h1>
            <p>Geselecteerde datum: {datum}</p>

            {/* Foutmelding tonen als er iets misgaat */}
            {error && <p className="error">{error}</p>}

            <div className="parking-grid">
                {loading ? (
                    <p>Parkeerplaatsen laden...</p>
                ) : parkeerplaatsen.length > 0 ? (
                    parkeerplaatsen.map((plek) => (
                        <div
                            key={plek.id}
                            className={`parkeerplaats ${plek.status}`} 
                            onClick={() => handleClick(plek.locatie)}
                        >
                            {plek.locatie}
                        </div>
                    ))
                ) : (
                    <p>Geen parkeerplaatsen gevonden voor de geselecteerde datum.</p>
                )}
            </div>
        </div>
    );
};

export default ParkeerplaatsenA;
