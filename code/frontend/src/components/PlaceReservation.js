import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import Swal from "sweetalert2";

const PlaceReservation = () => {
    const [voertuigen, setVoertuigen] = useState([]);
    const [selectedVoertuig, setSelectedVoertuig] = useState("");
    const [selectedParkeerplaats, setSelectedParkeerplaats] = useState("");
    const [starttijd, setStarttijd] = useState("");
    const [eindtijd, setEindtijd] = useState("");
    const [parkeerplaatsInfo, setParkeerplaatsInfo] = useState(null);
    const [error, setError] = useState("");

    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const plaatsLocatie = queryParams.get("plaatsLocatie");
    const datum = queryParams.get("datum");

    const navigate = useNavigate();

    useEffect(() => {
        fetchVoertuigen();
        if (plaatsLocatie) {
            setSelectedParkeerplaats(plaatsLocatie);
            fetchParkeerplaatsInfo(plaatsLocatie);
        }
        if (datum) {
            const defaultStarttijd = "12:00";
            const defaultEindtijd = "13:00";
            setStarttijd(defaultStarttijd);
            setEindtijd(defaultEindtijd);
            const startDate = new Date(`${datum}T${defaultStarttijd}`);
            startDate.setHours(startDate.getHours() + 1);
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

    const fetchParkeerplaatsInfo = async (plaatsId) => {
        try {
            const response = await axios.get("http://localhost:5000/api/parkings");
            const parkeerplaatsen = response.data;
            const parkeerplaats = parkeerplaatsen.find(p => p.locatie === plaatsId);
            if (parkeerplaats) {
                setParkeerplaatsInfo(parkeerplaats);
            } else {
                console.error("Geen parkeerplaats gevonden met locatie:", plaatsId);
            }
        } catch (error) {
            console.error("Fout bij ophalen parkeerplaats info:", error);
        }
    };

    const handleReservering = async () => {
        const userId = localStorage.getItem('user_id');
        if (!userId) {
            Swal.fire("Fout", "Gebruiker is niet ingelogd", "error");
            return;
        }

        const startDate = new Date(`${datum}T${starttijd}`);
        const endDate = new Date(`${datum}T${eindtijd}`);
        if ((endDate - startDate) < 3600000) {
            setError("Eindtijd moet minstens 1 uur na de starttijd zijn.");
            return;
        }

        const reservatieData = {
            gebruiker_id: userId,
            voertuig_id: selectedVoertuig,
            parkeerplaats_id: selectedParkeerplaats,
            starttijd: `${datum}T${starttijd}`,
            eindtijd: `${datum}T${eindtijd}`,
        };
        try {
            await axios.post(
                "http://localhost:5000/api/reservaties",
                reservatieData,
                { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
            );
            Swal.fire({
                title: "Reservering Succesvol!",
                text: "U wordt teruggestuurd naar het dashboard...",
                icon: "success",
                timer: 5000,
                showConfirmButton: false
            }).then(() => {
                navigate("/Dashboard");
            });
        } catch (error) {
            Swal.fire("Fout", "Fout bij reservering.", "error");
            console.error("Fout bij reserveren:", error);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="p-6 max-w-lg w-full border rounded-lg shadow-md bg-white">
                <h2 className="text-xl font-semibold mb-4 text-center">Maak een Reservering</h2>

                {error && <p className="text-red-500 mb-4 text-center">{error}</p>}

                <label>Voertuig</label>
                <select onChange={(e) => setSelectedVoertuig(e.target.value)} className="mb-4 w-full p-2 border rounded">
                    <option value="">Selecteer een voertuig</option>
                    {voertuigen.map((v) => (
                        <option key={v.nummerplaat} value={v.id}>{v.nummerplaat}</option>
                    ))}
                </select>

                <label>Parkeerplaats</label>
                <input type="text" value={selectedParkeerplaats} readOnly className="mb-4 w-full p-2 border rounded bg-gray-100" />

                <label>Starttijd</label>
                <input type="time" value={starttijd} onChange={(e) => setStarttijd(e.target.value)} className="mb-4 w-full p-2 border rounded" />

                <label>Eindtijd</label>
                <input type="time" value={eindtijd} onChange={(e) => setEindtijd(e.target.value)} className="mb-4 w-full p-2 border rounded" />

                <button className="mt-4 w-full p-2 bg-blue-500 text-white rounded" onClick={handleReservering}>Reserveren</button>

                {/* Terug-knop */}
                <button
                    className="mt-4 w-full p-2 bg-gray-500 text-white rounded"
                    onClick={() => navigate(-1)} // Dit stuurt de gebruiker terug naar de vorige pagina
                >
                    Terug
                </button>
            </div>
        </div>
    );
};

export default PlaceReservation;
