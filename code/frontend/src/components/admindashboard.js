import React, { useState, useEffect } from "react";
import './admin.css';

const AdminDashboard = () => {
    const [reserveringen, setReserveringen] = useState([]);
    const [statistieken, setStatistieken] = useState({});
    const [beschikbarePlaatsen, setBeschikbarePlaatsen] = useState(0);

    useEffect(() => {
        fetch("http://localhost:5000/api/reserveringen")
            .then((res) => res.json())
            .then((data) => setReserveringen(data));

        fetch("http://localhost:5000/api/statistieken")
            .then((res) => res.json())
            .then((data) => setStatistieken(data));

        fetch("http://localhost:5000/api/parkeerplaatsen")
            .then((res) => res.json())
            .then((data) => setBeschikbarePlaatsen(data.totaal_beschikbaar));

        // Statistieken updaten
        fetch("http://localhost:5000/api/update_statistieken", { method: "POST" });
    }, []);

    return (
        <div className="p-6 bg-gray-100 min-h-screen">
            <h1 className="text-2xl font-bold mb-4">Beheer Dashboard</h1>

            {/* Statistieken */}
            <div className="bg-white p-4 shadow rounded-lg mb-4">
                <h2 className="text-xl font-semibold">Statistieken</h2>
                <p><strong>Bezet:</strong> {statistieken.totaal_bezet}</p>
                <p><strong>Gemiddelde parkeertijd:</strong> {statistieken.gemiddelde_duur}</p>
                <p><strong>Totale inkomsten:</strong> €{statistieken.totale_inkomsten}</p>
            </div>

            {/* Beschikbare parkeerplaatsen */}
            <div className="bg-white p-4 shadow rounded-lg mb-4">
                <h2 className="text-xl font-semibold">Beschikbare Parkeerplaatsen</h2>
                <p className="text-2xl font-bold">{beschikbarePlaatsen}</p>
            </div>

            {/* Reserveringen */}
            <div className="bg-white p-4 shadow rounded-lg">
                <h2 className="text-xl font-semibold">Reserveringen</h2>
                <table className="w-full border-collapse border">
                    <thead>
                        <tr className="bg-gray-200">
                            <th className="border p-2">Nummer</th>
                            <th className="border p-2">Starttijd</th>
                            <th className="border p-2">Eindtijd</th>
                            <th className="border p-2">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reserveringen.map((res) => (
                            <tr key={res.id}>
                                <td className="border p-2">{res.reservatienummer}</td>
                                <td className="border p-2">{res.starttijd}</td>
                                <td className="border p-2">{res.eindtijd}</td>
                                <td className="border p-2">{res.status}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminDashboard;
