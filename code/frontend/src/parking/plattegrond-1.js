import React from "react";
import { Link } from "react-router-dom"; // Importeer Link voor navigatie
import "./ParkingMap.css"; // Zorg ervoor dat deze CSS bestaat of gebruik Tailwind

// Configuratie voor de zones (ID, kleur, link)
const zones = [
    { id: "A", color: "red", link: "/parkeerplaatsen" },
    { id: "B", color: "orange", link: "/parkeerplaatsen" },
    { id: "C", color: "yellow", link: "/parkeerplaatsen" },
    { id: "D", color: "green", link: "/parkeerplaatsen" },
    { id: "E", color: "lightblue", link: "/parkeerplaatsen" },
    { id: "F", color: "indigo", link: "/parkeerplaatsen" },
    { id: "G", color: "violet", link: "/parkeerplaatsen" },
    { id: "H", color: "brown", link: "/parkeerplaatsen" },
    { id: "I", color: "gray", link: "/parkeerplaatsen" },
];

const Plattegrond1 = () => {
    // Haal de datum op uit de queryparameter
    const urlParams = new URLSearchParams(window.location.search);
    const datum = urlParams.get('datum'); // Haal de datum op uit de queryparameter

    return (
        <div className="parking-container">
            {/* Toon de geselecteerde datum en de hardcoded verdieping */}
            <div className="info-container">
                {datum && <p><strong>Geselecteerde datum:</strong> {datum}</p>}
                <p><strong>Verdieping:</strong> -1</p>
            </div>

            <div className="parking">
                {/* Render alle zones met een dynamische map */}
                {zones.map((zone) => (
                    <div
                        key={zone.id}
                        className="zone"
                        style={{ backgroundColor: zone.color }} // Kleur per zone
                    >
                        {/* Voeg de datum en zone als queryparameters toe aan de zone-link */}
                        <Link to={`${zone.link}?datum=${datum}&zone=${zone.id}`} className="zone-link">
                            Zone {zone.id}
                        </Link>
                    </div>
                ))}
            </div>

            {/* Terugknop */}
            <button
                onClick={() => window.history.back()}
                className="back-button"
            >
                Terug
            </button>
        </div>
    );
};

export default Plattegrond1;
