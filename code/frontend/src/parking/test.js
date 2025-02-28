import React from "react";
import { Link } from "react-router-dom"; // Importeer Link voor navigatie
import "./ParkingMap.css"; // Zorg ervoor dat deze CSS bestaat of gebruik Tailwind

const zones = [
    { id: "A", color: "red", link: "/parkeerplaatsen-a" }, // Link naar de pagina voor Zone A
    { id: "B", color: "orange", link: "/parkeerplaatsen-b" },
    { id: "C", color: "yellow", link: "/parkeerplaatsen-c" },
    { id: "D", color: "green", link: "/parkeerplaatsen-d" },
    { id: "E", color: "blue", link: "/parkeerplaatsen-e" },
    { id: "F", color: "indigo", link: "/parkeerplaatsen-f" },
    { id: "G", color: "violet", link: "/parkeerplaatsen-g" },
    { id: "H", color: "brown", link: "/parkeerplaatsen-h" },
    { id: "I", color: "gray", link: "/parkeerplaatsen-i" },
];

const Plattegrond1 = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const datum = urlParams.get('datum'); // Haal de datum op uit de queryparameter

    return (
        <div className="parking-container">
            <div className="parking">
                {zones.map((zone) => (
                    <div
                        key={zone.id}
                        className="zone"
                        style={{ backgroundColor: zone.color }}
                    >
                        {/* Voeg de datum als queryparameter toe aan de zone-link */}
                        <Link to={`${zone.link}?datum=${datum}`} className="zone-link">
                            {zone.id}
                        </Link>
                    </div>
                ))}
            </div>

            {/* Terugknop */}
            <button
                onClick={() => window.history.back()}
                className="back-button"
            >
                Terug naar vorige pagina
            </button>
        </div>
    );
};

export default Plattegrond1;
