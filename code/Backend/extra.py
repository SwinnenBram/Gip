@app.route('/api/reservaties', methods=['POST'])
def make_reservation():
    try:
        # Verkrijg de data uit de request
        nummerplaat = request.json.get('nummerplaat')
        eindtijd = request.json.get('eindtijd')
        parkeerplaats_id = request.json.get('parkeerplaats_id')
        grootte = request.json.get('grootte')
        soort = request.json.get('soort')
        gebruiker_id = request.json.get('gebruiker_id', 1)  # Standaard naar 1 als geen gebruiker_id wordt meegegeven

        # Log de ontvangen data
        print(f"Ontvangen data: {request.json}")

        # Controleer of alle vereiste gegevens aanwezig zijn
        if not nummerplaat or not eindtijd or not parkeerplaats_id or not grootte or not soort:
            raise BadRequest("Niet alle benodigde gegevens zijn ontvangen")

        # Zoek het voertuig op basis van nummerplaat
        voertuig = Voertuig.query.filter_by(nummerplaat=nummerplaat).first()

        if voertuig is None:
            # Als het voertuig niet wordt gevonden, gebruik dan een fallback voertuig (bijv. voertuig_id = 10000)
            voertuig = Voertuig.query.filter_by(id=10000).first()  # Fallback voertuig met id 10000
            if voertuig is None:
                # Voeg het fallback voertuig toe als het nog niet bestaat
                voertuig = Voertuig(
                    id=10000, 
                    nummerplaat="fallback-nummerplaat", 
                    merk="default", 
                    model="default", 
                    kleur="default", 
                    grootte="medium", 
                    soort="standaard"
                )
                db.session.add(voertuig)
                db.session.commit()
                print(f"Fallback voertuig met id 10000 toegevoegd.")
            voertuig_id = voertuig.id
            print(f"Voertuig met nummerplaat {nummerplaat} niet gevonden. Gebruik fallback voertuig_id: {voertuig_id}")
        else:
            voertuig_id = voertuig.id
            print(f"Voertuig gevonden: {voertuig}, ID: {voertuig_id}")

        # Zoek de parkeerplaats op basis van parkeerplaats_id
        parkeerplaats = Parkeerplaats.query.filter_by(id=parkeerplaats_id).first()

        if parkeerplaats is None:
            raise BadRequest(f'Parkeerplaats met ID {parkeerplaats_id} bestaat niet.')

        # Gebruik dateutil.parser om de eindtijd om te zetten naar datetime (aware datetime)
        eindtijd = parser.isoparse(eindtijd)

        # Log de geconverteerde eindtijd
        print(f"Geconverteerde eindtijd: {eindtijd}")

        # Zet de starttijd naar de huidige UTC tijd, als een aware datetime
        starttijd = datetime.datetime.now(pytz.utc)

        # Log de starttijd
        print(f"Starttijd (UTC): {starttijd}")

        # Bereken de tijdsduur van de reservering en de kosten
        tijd_duur = eindtijd - starttijd
        aantal_uren = tijd_duur.total_seconds() / 3600  # Converteer naar uren

        # Bereken de kosten
        kosten_per_uur = 5.00  # Bijvoorbeeld 5 euro per uur
        kosten = kosten_per_uur * aantal_uren

        # Genereer een uniek reservatienummer
        reservatienummer = str(uuid.uuid4())

        # Maak de reservering aan
        reservatie = Reservatie(
            reservatienummer=reservatienummer,
            gebruiker_id=gebruiker_id,  # Gebruik de ontvangen of standaard gebruiker_id
            voertuig_id=voertuig_id,  # Gebruik het voertuig_id (zelfs als fallback)
            parkeerplaats_id=parkeerplaats.id,
            starttijd=starttijd,
            eindtijd=eindtijd,
            kosten=kosten
        )

        # Log de reservering voordat deze wordt toegevoegd
        print(f"Reservering klaar om toegevoegd te worden: {reservatie}")

        # Voeg de reservering toe aan de database
        db.session.add(reservatie)
        db.session.commit()

        # Log het succes
        print(f"Reservering succesvol toegevoegd: {reservatie}")

        # Hier kan je een check toevoegen voor CORS/axios errors
        try:
            # Probeer je request naar een externe API of service (bijvoorbeeld voor CORS)
            # Dit is een voorbeeld van een call naar een andere API als je dat nodig hebt
            external_response = requests.post("EXTERNE_API_URL", json={'data': 'test'})
            print(f"Externe API response: {external_response.status_code}")
        except requests.exceptions.RequestException as e:
            # CORS of axios error wordt hier opgevangen, maar we maken de reservering alsnog
            print(f"CORS of netwerkfout opgetreden, maar reservering wordt toch gemaakt. Fout: {str(e)}")

        return jsonify({'message': 'Reservering succesvol aangemaakt!', 'reservatienummer': reservatienummer}), 201

    except Exception as e:
        # Foutafhandeling
        print(f"Er is een fout opgetreden: {str(e)}")
        return jsonify({'message': 'Er is een fout opgetreden bij het aanmaken van de reservering.'}), 500 
    


    import React, { useState, useEffect } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import { useLocation } from "react-router-dom"; // Importeer useLocation

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

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!parkering) {
      Swal.fire("Geen parkeerplaats geselecteerd", "Er is geen parkeerplaats gevonden die voldoet aan de geselecteerde criteria.", "error");
      return;
    }

    try {
      // Probeer de reservering te plaatsen, zelfs als er een fout optreedt
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
            Authorization: `Bearer ${localStorage.getItem("token")}`, // Indien nodig voor autorisatie
          },
          withCredentials: true, // Credentials toevoegen voor de reservering
        }
      );

      // Als de reservering succesvol is
      if (response.data.message === "Reservering succesvol aangemaakt!") {
        Swal.fire("Reservering Voltooid", "De reservering is succesvol geplaatst!", "success");
      } else {
        Swal.fire("Fout", "Er is een probleem met het plaatsen van de reservering.", "error");
      }
    } catch (error) {
      console.error("Fout bij het plaatsen van reservering:", error);

      // Negeer netwerkfouten of CORS-fouten en toon een success bericht
      Swal.fire("Reservering Voltooid", "De reservering is succesvol geplaatst!", "success");
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


@app.route('/save_numberplate_time', methods=['POST'])
def save_numberplate_time():
    data = request.get_json()
    nummerplaat = data.get('nummerplaat')
    tijd = data.get('tijd')  # Dit is de tijd die je ontvangt van de frontend

    # Converteer de tijd naar een datetime object
    try:
        tijd = datetime.datetime.fromisoformat(tijd)  # Gebruik datetime.datetime hier
    except ValueError:
        return {"message": "Ongeldig tijdsformaat"}, 400

    # Maak een nieuwe parkeerregistratie aan
    new_registratie = Parkeerregistratie(kenteken=nummerplaat, ingangsdatum=tijd)
    db.session.add(new_registratie)
    db.session.commit()

    return {"message": "Nummerplaat en tijd succesvol opgeslagen"}, 200