import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Parkeerplaatsen.css";

const Parkeerplaatsen = () => {
    const [parkeerplaatsen, setParkeerplaatsen] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [infoMessage, setInfoMessage] = useState(null); // State voor info bericht

    const navigate = useNavigate();
    const location = useLocation();

    // Haal de datum en zone op uit de queryparameters
    const urlParams = new URLSearchParams(location.search);
    const datum = urlParams.get("datum");
    const zone = urlParams.get("zone");

    useEffect(() => {
        if (datum && zone) {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem("token");

            // Bepaal de juiste locatie range op basis van de zone
            let locatieRange = [];
            if (zone === "A") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `A${i + 1}`);
            } else if (zone === "B") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `B${i + 1}`);
            } else if (zone === "C") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `C${i + 1}`);
            } else if (zone === "D") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `D${i + 1}`);
            } else if (zone === "E") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `E${i + 1}`);
            } else if (zone === "F") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `F${i + 1}`);
            } else if (zone === "G") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `G${i + 1}`);
            } else if (zone === "H") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `H${i + 1}`);
            } else if (zone === "I") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `I${i + 1}`);
            } else if (zone === "J") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `J${i + 1}`);
            } else if (zone === "K") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `K${i + 1}`);
            } else if (zone === "L") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `L${i + 1}`);
            } else if (zone === "M") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `M${i + 1}`);
            } else if (zone === "N") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `N${i + 1}`);
            } else if (zone === "O") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `O${i + 1}`);
            } else if (zone === "P") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `P${i + 1}`);
            } else if (zone === "Q") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `Q${i + 1}`);
            } else if (zone === "R") {
                locatieRange = Array.from({ length: 40 }, (_, i) => `R${i + 1}`);
            }

            // Haal parkeerplaatsen op voor de geselecteerde zone en datum
            axios
                .get(`http://localhost:5000/api/parkings?datum=${datum}&zone=${zone}`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                })
                .then((response) => {
                    // Filter parkeerplaatsen op basis van de locatie range voor de geselecteerde zone
                    const filteredParkeerplaatsen = response.data.filter(plek =>
                        locatieRange.includes(plek.locatie)
                    );

                    const parkeerplaatsenData = filteredParkeerplaatsen.map((plek) => ({
                        id: plek.id,
                        locatie: plek.locatie,
                        status: "beschikbaar", // Standaard status
                    }));

                    // Haal reserveringen op voor de geselecteerde datum
                    axios
                        .get(`http://localhost:5000/api/reservaties/op_datum?datum=${datum}`, {
                            headers: {
                                Authorization: `Bearer ${token}`,
                            },
                        })
                        .then((res) => {
                            const gereserveerdePlekken = res.data.map(
                                (reservatie) => reservatie.parkeerplaats_id
                            );

                            // Update de parkeerplaatsen met de status 'gereserveerd' of 'beschikbaar'
                            const updatedParkeerplaatsen = parkeerplaatsenData.map((plek) => ({
                                ...plek,
                                status: gereserveerdePlekken.includes(plek.id)
                                    ? "gereserveerd"
                                    : "beschikbaar",
                            }));

                            setParkeerplaatsen(updatedParkeerplaatsen);
                        })
                        .catch((err) => {
                            console.error("Fout bij het ophalen van reserveringen:", err);
                            setError("Geen parkeerplaatsen gereserveerd.");
                            setParkeerplaatsen(parkeerplaatsenData); // In geval van fout, parkeerplaatsen toch weergeven
                        })
                        .finally(() => {
                            setLoading(false);
                        });
                })
                .catch((err) => {
                    console.error("Fout bij het ophalen van parkeerplaatsen:", err);
                    setError("Kan parkeerplaatsen niet laden.");
                    setLoading(false);
                });
        }
    }, [datum, zone]);

    const handleClick = (locatie, status) => {
        if (status === "gereserveerd") {
            setInfoMessage("Parkeerplaats is al gereserveerd");
        } else {
            navigate(`/place-reservation?plaatsLocatie=${locatie}&datum=${datum}`);
        }
    };

    const handleBackClick = () => {
        // Terug navigeren naar de vorige pagina
        navigate(-1); // Dit zorgt ervoor dat de gebruiker terug gaat naar de vorige pagina
    };

    return (
        <div className="container">
            <h1 className="title">Parkeerplaatsen - Zone {zone}</h1>
            <p>Geselecteerde datum: {datum}</p>
            {error && <p className="error">{error}</p>}
            {infoMessage && <p className="info-message">{infoMessage}</p>} {/* Info bericht tonen */}

            {/* Terug knop */}
            <button
                onClick={handleBackClick}
                className="back-button"
            >
                Terug
            </button>

            <div className="parking-grid">
                {loading ? (
                    <p>Parkeerplaatsen laden...</p>
                ) : (
                    parkeerplaatsen.map((plek) => (
                        <div
                            key={plek.id}
                            className={`parkeerplaats ${plek.status}`}
                            onClick={() => handleClick(plek.locatie, plek.status)} // Pass status door
                        >
                            {plek.locatie}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Parkeerplaatsen;
