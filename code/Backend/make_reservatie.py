@app.route('/api/reservaties', methods=['POST'])
def create_reservatie():
    data = request.get_json()
    gebruiker_id = data.get('gebruiker_id')  # Verkrijg de gebruiker_id uit de request
    voertuig_nummerplaat = data.get('voertuig_id')  # Zorg ervoor dat dit klopt
    parkeerplaats_id = data.get('parkeerplaats_id')  # Verkrijg de locatiecode van de parkeerplaats (zoals 'A15')
    starttijd = data.get('starttijd')
    eindtijd = data.get('eindtijd')

    try:
        # Log de ontvangen data voor debugging
        print(f"Ontvangen data: {data}")
        print(f"Zoeken naar voertuig met nummerplaat: {voertuig_nummerplaat}")

        # Zoek het voertuig op basis van de nummerplaat
        voertuig = Voertuig.query.filter_by(nummerplaat=voertuig_nummerplaat).first()

        # Log de query resultaat
        print(f"Query resultaat: {voertuig}")

        if voertuig is None:
            print("Voertuig niet gevonden.")
            return jsonify({'message': 'Voertuig niet gevonden op nummerplaat'}), 400

        voertuig_id = voertuig.id
        print(f"Voertuig gevonden: {voertuig}, ID: {voertuig_id}")

        # Zoek de parkeerplaats op basis van de locatiecode (bijvoorbeeld 'A15')
        parkeerplaats = Parkeerplaats.query.filter_by(locatie=parkeerplaats_id).first()

        if parkeerplaats is None:
            print(f"Fout: Parkeerplaats met locatiecode {parkeerplaats_id} bestaat niet.")
            return jsonify({'message': f'Parkeerplaats {parkeerplaats_id} bestaat niet.'}), 400

        # Verkrijg de id van de gevonden parkeerplaats
        parkeerplaats_id = parkeerplaats.id
        print(f"Parkeerplaats gevonden: {parkeerplaats}, ID: {parkeerplaats_id}")

        # Converteer de tijd naar datetime objecten
        starttijd = datetime.datetime.strptime(starttijd, '%Y-%m-%dT%H:%M')
        eindtijd = datetime.datetime.strptime(eindtijd, '%Y-%m-%dT%H:%M')

        # Log de geconverteerde tijden
        print(f"Starttijd: {starttijd}, Eindtijd: {eindtijd}")

        # Bereken de kosten
        kosten_per_uur = 5.00
        tijd_duur = eindtijd - starttijd
        aantal_uren = tijd_duur.total_seconds() / 3600  # Converteer naar uren
        kosten = kosten_per_uur * aantal_uren

        # Genereer een uniek reservatienummer
        reservatienummer = str(uuid.uuid4())

        # Maak de reservering
        reservatie = Reservatie(
            reservatienummer=reservatienummer,
            gebruiker_id=gebruiker_id,  # Gebruik de ontvangen gebruiker_id
            voertuig_id=voertuig_id,
            parkeerplaats_id=parkeerplaats_id,
            starttijd=starttijd,
            eindtijd=eindtijd,
            kosten=kosten
        )

        # Log de reservering voor het toevoegen aan de database
        print(f"Reservering klaar om toegevoegd te worden: {reservatie}")

        db.session.add(reservatie)
        db.session.commit()

        gebruiker = Gebruiker.query.get(gebruiker_id)
        if gebruiker and gebruiker.email:
            send_reservation_email(
                reservering=reservatie,
                nummerplaat=voertuig_nummerplaat,
                locatie=parkeerplaats.locatie,
                email=gebruiker.email
            )

        # Log succesvolle toevoeging
        print(f"Reservering succesvol toegevoegd: {reservatie}")

        return jsonify({'message': 'Reservering succesvol aangemaakt!'}), 201

    except Exception as e:
        db.session.rollback()
        # Log de fout
        print(f"Fout bij het maken van de reservering: {str(e)}")
        return jsonify({'message': 'Fout bij het maken van de reservering', 'error': str(e)}), 500