import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./Parkeerplaatsen.css";

const ParkeerplaatsenA = () => {
    const [parkeerplaatsen, setParkeerplaatsen] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    const urlParams = new URLSearchParams(location.search);
    const datum = urlParams.get("datum");

    useEffect(() => {
        if (datum) {
            setLoading(true);
            setError(null);
    
            const token = localStorage.getItem("token");
    
            // 🚗 **Stap 1: Haal parkeerplaatsen op**
            axios.get(`http://localhost:5000/api/parkings?datum=${datum}&zone=A`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then((response) => {
                    const parkeerplaatsenData = response.data.map(plek => ({
                        id: plek.id,
                        locatie: plek.locatie,
                        status: 'beschikbaar' // Standaard groen
                    }));
    
                    // 🚗 **Stap 2: Haal reserveringen op voor de geselecteerde datum**
                    axios.get(`http://localhost:5000/api/reservaties/op_datum?datum=${datum}`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    })
                        .then((res) => {
                            const gereserveerdePlekken = res.data.map(reservatie => reservatie.parkeerplaats_id);
                            console.log(`Gereserveerde parkeerplaatsen op ${datum}:`, gereserveerdePlekken);
    
                            // 🚗 **Stap 3: Update status van gereserveerde plekken**
                            const updatedParkeerplaatsen = parkeerplaatsenData.map(plek => ({
                                ...plek,
                                status: gereserveerdePlekken.includes(plek.id) ? 'gereserveerd' : 'beschikbaar'
                            }));
    
                            setParkeerplaatsen(updatedParkeerplaatsen);
                        })
                        .catch((err) => {
                            console.error("❌ Fout bij het ophalen van reserveringen:", err);
                            setError("Kan reserveringsgegevens niet laden.");
                        })
                        .finally(() => {
                            setLoading(false);
                        });
                })
                .catch((err) => {
                    console.error("❌ Fout bij het ophalen van parkeerplaatsen:", err);
                    setError("Kan parkeerplaatsen niet laden.");
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
            {error && <p className="error">{error}</p>}
            <div className="parking-grid">
                {loading ? (
                    <p>Parkeerplaatsen laden...</p>
                ) : (
                    parkeerplaatsen.map((plek) => (
                        <div
                            key={plek.id}
                            className={`parkeerplaats ${plek.status}`}
                            onClick={() => handleClick(plek.locatie)}
                        >
                            {plek.locatie}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ParkeerplaatsenA;
