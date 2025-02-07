import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom"; // Importeer useLocation voor het ophalen van de queryparameters
import axios from "axios";
import "./Parkeerplaatsen.css";

const ParkeerplaatsenA = () => {
    const [parkeerplaatsen, setParkeerplaatsen] = useState([]);
    const navigate = useNavigate();
    const location = useLocation(); // Verkrijg de huidige locatie van de URL

    // Haal de datum op uit de queryparameter
    const urlParams = new URLSearchParams(location.search);
    const datum = urlParams.get("datum"); // Datum uit de URL queryparameter

    useEffect(() => {
        // Haal de parkeerplaatsen op van de API, inclusief datum in de queryparameters
        if (datum) {
            axios.get(`http://localhost:5000/api/parkings?datum=${datum}&zone=A`)
                .then((response) => {
                    setParkeerplaatsen(response.data); // Sla de parkeerplaatsen op
                })
                .catch((error) => {
                    console.error("Fout bij het ophalen van parkeerplaatsen:", error);
                });
        }
    }, [datum]); // Effect triggeren wanneer de datum verandert

    const handleClick = (locatie) => {
        // Navigeren naar place-reservation en de locatie van de parkeerplaats meegeven
        navigate(`/place-reservation?plaatsLocatie=${locatie}&datum=${datum}`);  // Hier wordt de datum meegegeven
    };

    return (
        <div className="container">
            <h1 className="title">Parkeerplaatsen - Zone A</h1>
            <p>Geselecteerde datum: {datum}</p> {/* Toon de geselecteerde datum */}

            <div className="parking-grid">
                {/* Render de parkeerplaatsen met locatie in plaats van id */}
                {parkeerplaatsen.length > 0 ? (
                    parkeerplaatsen.map((plek) => (
                        <div
                            key={plek.id}
                            className={`parkeerplaats ${plek.status}`} 
                            onClick={() => handleClick(plek.locatie)} // Klik event toevoegen en locatie doorgeven
                        >
                            {/* Toon de locatie zoals "A10", "A11", etc. */}
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
