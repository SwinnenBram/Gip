import React from "react";
import { Link } from "react-router-dom"; // Importeer Link voor navigatie
import "./ParkingMap.css"; // Zorg ervoor dat deze CSS bestaat of gebruik Tailwind

const zones = [
    { id: "A", color: "red", link: "/parkeerplaatsen-a" }, // Link naar de pagina voor Zone A
    { id: "B", color: "orange", link: "/reserveren-b" },
    { id: "C", color: "yellow", link: "/reserveren-c" },
    { id: "D", color: "green", link: "/reserveren-d" },
    { id: "E", color: "blue", link: "/reserveren-e" },
    { id: "F", color: "indigo", link: "/reserveren-f" },
    { id: "G", color: "violet", link: "/reserveren-g" },
    { id: "H", color: "brown", link: "/reserveren-h" },
    { id: "I", color: "gray", link: "/reserveren-i" },
];

const Plattegrond1 = () => {
    return (
        <div className="parking-container">
            <div className="parking">
                {zones.map((zone) => (
                    <div
                        key={zone.id}
                        className="zone"
                        style={{ backgroundColor: zone.color }}
                    >
                        <Link to={zone.link} className="zone-link">
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
