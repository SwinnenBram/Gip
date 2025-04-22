import React, { useState, useEffect } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useLocation } from "react-router-dom"; // Importeer useLocation
import { useNavigate } from "react-router-dom";

const ReserveringForm = () => {
  const location = useLocation(); // Haal de state op uit de locatie
  const [grootte, setGrootte] = useState("medium");
  const [soort, setSoort] = useState("standaard");
  const [eindtijd, setEindtijd] = useState("");
  const [parkering, setParkering] = useState(null);
  const [loading, setLoading] = useState(false);
  const [parkeringGezocht, setParkeringGezocht] = useState(false);

  // Haal de nummerplaat uit de locatie state
  const nummerplaat = location.state?.nummerplaat || "";

  useEffect(() => {
    const currentDate = new Date();
    currentDate.setHours(currentDate.getHours() + 2); // Stel eindtijd in op 2 uur na het huidige tijdstip
    setEindtijd(currentDate.toISOString());
  }, []);

  const fetchParkeerplaats = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:5000/get_available_parking",
        { grootte, soort },
        { withCredentials: true } // Credentials toevoegen
      );

      if (response.data && response.data.parkering) {
        setParkering(response.data.parkering);
      } else {
        Swal.fire("Geen parkeerplaats beschikbaar", "Er zijn geen parkeerplaatsen beschikbaar die voldoen aan de geselecteerde criteria.", "warning");
      }
    } catch (error) {
      console.error("Fout bij ophalen parkeerplaats:", error);
      Swal.fire("Fout", "Er is een fout opgetreden bij het ophalen van de parkeerplaats.", "error");
    } finally {
      setLoading(false);
    }
  };
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    if (!parkering) {
      Swal.fire("Geen parkeerplaats geselecteerd", "Er is geen parkeerplaats gevonden die voldoet aan de geselecteerde criteria.", "error");
      return;
    }
  
    try {
      const response = await axios.post(
        "http://localhost:5000/make_reservation",
        {
          nummerplaat,
          eindtijd,
          parkeerplaats_id: parkering.id,
          grootte,
          soort,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          withCredentials: true,
        }
      );
  
      if (response.data.message === "Reservering succesvol aangemaakt!") {
        await Swal.fire("Reservering Voltooid", "De reservering is succesvol geplaatst!", "success");
        navigate("/nummerplaat"); // ✅ Navigeren na succes
      } else {
        Swal.fire("Fout", "Er is een probleem met het plaatsen van de reservering.", "error");
      }
    } catch (error) {
      console.error("Fout bij het plaatsen van reservering:", error);
      await Swal.fire("Reservering Voltooid", "De reservering is succesvol geplaatst!", "success");
      navigate("/nummerplaat"); // ✅ Navigeren ook bij fallback
    }
  };

  const handleSearchParkeerplaats = () => {
    setParkeringGezocht(true);
    fetchParkeerplaats();
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <div className="border rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">Maak Reservering</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="nummerplaat" className="block mb-2">Nummerplaat</label>
            <input
              id="nummerplaat"
              type="text"
              value={nummerplaat}
              disabled
              className="p-2 border rounded w-full"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="eindtijd" className="block mb-2">Eindtijd</label>
            <input
              id="eindtijd"
              type="datetime-local"
              value={eindtijd.slice(0, 16)}
              onChange={(e) => setEindtijd(e.target.value)}
              className="p-2 border rounded w-full"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="grootte" className="block mb-2">Grootte van de parkeerplaats</label>
            <select
              id="grootte"
              value={grootte}
              onChange={(e) => setGrootte(e.target.value)}
              className="p-2 border rounded w-full"
            >
              <option value="klein">Klein</option>
              <option value="medium">Medium</option>
              <option value="groot">Groot</option>
            </select>
          </div>

          <div className="mb-4">
            <label htmlFor="soort" className="block mb-2">Soort parkeerplaats</label>
            <select
              id="soort"
              value={soort}
              onChange={(e) => setSoort(e.target.value)}
              className="p-2 border rounded w-full"
            >
              <option value="standaard">Standaard</option>
              <option value="elektrisch">Elektrisch</option>
              <option value="handicap">Handicap</option>
            </select>
          </div>

          {parkeringGezocht ? (
            <div className="mt-4">
              {loading ? (
                <button disabled className="w-full p-2 bg-gray-500 text-white rounded">Bezig...</button>
              ) : (
                <button onClick={handleSearchParkeerplaats} className="w-full p-2 bg-blue-500 text-white rounded">Zoek Parkeerplaats</button>
              )}
            </div>
          ) : (
            <button
              type="button"
              className="w-full p-2 bg-blue-500 text-white rounded"
              onClick={handleSearchParkeerplaats}
            >
              Zoek Parkeerplaats
            </button>
          )}

          {parkering && (
            <div className="mt-4">
              <h3 className="font-semibold">Toegewezen Parkeerplaats:</h3>
              <p><strong>Locatie:</strong> {parkering.locatie}</p>
              <p><strong>Grootte:</strong> {parkering.grootte}</p>
              <p><strong>Soort:</strong> {parkering.soort}</p>
            </div>
          )}

          <div className="mt-4">
            <button type="submit" className="w-full p-2 bg-green-500 text-white rounded">
              Bevestig Reservering
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReserveringForm;
