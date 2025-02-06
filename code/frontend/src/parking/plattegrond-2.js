import React from "react";
import "./ParkingMap.css"; // Zorg dat deze CSS bestaat of gebruik Tailwind

const zones = [
    { id: "ddd", color: "bg-red-500" },
    { id: "B", color: "bg-orange-500" },
    { id: "C", color: "bg-yellow-500" },
    { id: "D", color: "bg-green-500" },
    { id: "E", color: "bg-blue-500" },
    { id: "F", color: "bg-indigo-500" },
    { id: "G", color: "bg-violet-500" },
    { id: "H", color: "bg-brown-500" },
    { id: "I", color: "bg-gray-500" },
];

const Plattegrond1 = () => {
    return (
        <div className="flex flex-wrap gap-4 p-6 max-w-2xl mx-auto bg-white rounded-xl shadow-md">
            <h1 className="w-full text-xl font-bold text-center">Plattegrond Verdiep -1</h1>
            <div className="grid grid-cols-3 gap-4 w-full">
                {zones.map((zone) => (
                    <div 
                        key={zone.id} 
                        className={`p-6 text-white text-center font-semibold rounded-lg ${zone.color}`}
                    >
                        {zone.id}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Plattegrond1;
