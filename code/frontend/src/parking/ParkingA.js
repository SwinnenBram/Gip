import React from "react";
import "./Parkeerplaatsen.css"; // Zorg ervoor dat deze CSS beschikbaar is

const parkeerplaatsen = Array.from({ length: 40 }, (_, index) => ({
    id: index + 1,
    status: Math.random() < 0.5 ? "beschikbaar" : "bezet", // Willekeurige status: 50% beschikbaar, 50% bezet
}));

const ParkeerplaatsenA = () => {
    return (
        <div className="container">
            <h1 className="title">Parkeerplaatsen - Zone A</h1>
            <div className="parking-grid">
                {/* Render parkeerplaatsen */}
                {parkeerplaatsen.map((plek) => (
                    <div
                        key={plek.id}
                        className={`parkeerplaats ${plek.status}`}
                    >
                        {plek.id}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ParkeerplaatsenA;
