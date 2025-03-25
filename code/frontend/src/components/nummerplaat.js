import React, { useState } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useNavigate } from "react-router-dom";

const CheckReservering = () => {
  const [nummerplaat, setNummerplaat] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleNummerplaatChange = (e) => {
    setNummerplaat(e.target.value);
  };

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const uploadAndExtractNumberplate = async () => {
    if (!image) {
      Swal.fire("Fout!", "Upload alstublieft een afbeelding.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("image", image);

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/upload_image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data.nummerplaat) {
        setNummerplaat(response.data.nummerplaat);
        Swal.fire("Gevonden!", `Nummerplaat: ${response.data.nummerplaat}`, "success");
      } else {
        Swal.fire("Geen nummerplaat gevonden", "Probeer een andere afbeelding.", "warning");
      }
    } catch (error) {
      console.error("Fout bij uploaden:", error);
      Swal.fire("Fout", "Er is een fout opgetreden bij het verwerken van de afbeelding.", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchReservering = async () => {
    if (!nummerplaat) {
      Swal.fire("Fout!", "Vul alstublieft een nummerplaat in.", "error");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:5000/check_numberplate",
        { nummerplaat },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );

      if (!response.data || response.data.status === "not_found") {
        Swal.fire({
          title: "❌ Geen Reservering Gevonden",
          text: "Er is geen reservering gevonden voor deze nummerplaat.",
          icon: "warning",
          showCancelButton: true,
          cancelButtonText: "Sluiten",
          confirmButtonText: "Wilt u reserveren?",
        }).then((result) => {
          if (result.isConfirmed) {
            navigate("/reserveerd_direct", { state: { nummerplaat } });
            Swal.fire("Reserveren", "Je wordt doorgestuurd naar het reserveringsformulier.", "info");
          }
        });
        return;
      }

      let eindtijd = new Date(response.data.eindtijd);
      let starttijd = new Date(response.data.starttijd);

      Swal.fire({
        title: "✅ Reservering Gevonden",
        html: ` 
          <p><strong>📍 Locatie:</strong> ${response.data.locatie}</p>
          <p><strong>⏳ Eindtijd:</strong> ${eindtijd.toLocaleTimeString()}</p>
        `,
        icon: "success",
        confirmButtonText: "OK",
      });

      const currentTime = new Date().toISOString();
      await axios.post(
        "http://localhost:5000/save_numberplate_time",
        { nummerplaat, tijd: currentTime },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      console.log("✅ Nummerplaat en tijd opgeslagen");
    } catch (error) {
      console.error("⚠️ Fout bij ophalen reservering:", error);
      Swal.fire("Fout", "Er is een fout opgetreden bij het ophalen van de reservering.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <div className="border rounded-lg p-6 shadow-md">
        <h2 className="text-xl font-semibold mb-4">Controleer Reservering</h2>

        <div className="mt-4">
          <label htmlFor="nummerplaat" className="block">Nummerplaat</label>
          <input
            id="nummerplaat"
            type="text"
            value={nummerplaat}
            onChange={handleNummerplaatChange}
            className="p-2 border rounded w-full"
            placeholder="Voer nummerplaat in"
          />

          <label className="block mt-4">Upload een afbeelding:</label>
          <input type="file" onChange={handleImageChange} className="p-2 border rounded w-full" />

          <button 
            onClick={uploadAndExtractNumberplate} 
            className="mt-4 w-full p-2 bg-green-500 text-white rounded"
            disabled={loading}
          >
            {loading ? "Verwerken..." : "Nummerplaat Uit Afbeelding"}
          </button>

          <button 
            onClick={fetchReservering} 
            className="mt-4 w-full p-2 bg-blue-500 text-white rounded"
            disabled={loading || !nummerplaat}
          >
            {loading ? "Bezig..." : "Zoek Reservatie"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CheckReservering;
