import React, { useEffect, useState } from "react";
import axios from "axios";  // Zorg ervoor dat axios geïnstalleerd is
import "./Parkeerplaatsen.css";

const ParkeerplaatsenA = () => {
    const [parkeerplaatsen, setParkeerplaatsen] = useState([]);

    useEffect(() => {
        // Haal de parkeerplaatsen op van de API
        axios.get("http://localhost:5000/api/parkings")
            .then((response) => {
                setParkeerplaatsen(response.data);
            })
            .catch((error) => {
                console.error("Fout bij het ophalen van parkeerplaatsen:", error);
            });
    }, []);

    return (
        <div className="container">
            <h1 className="title">Parkeerplaatsen - Zone A</h1>
            <div className="parking-grid">
                {/* Render parkeerplaatsen */}
                {parkeerplaatsen.map((plek) => (
                    <div
                        key={plek.id}
                        className={`parkeerplaats ${plek.status}`} // Gebruik de status uit de API
                    >
                        {plek.id}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ParkeerplaatsenA;
