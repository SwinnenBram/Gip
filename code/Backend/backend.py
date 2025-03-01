from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import smtplib
from email.mime.text import MIMEText
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import uuid
import datetime


app = Flask(__name__)
CORS(app, origins=["http://localhost:3001"], supports_credentials=True)

# Database configuratie
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/parkeergarage_beheer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definieer database modellen
class Gebruiker(db.Model):
    __tablename__ = 'Gebruikers'
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefoonnummer = db.Column(db.String(15))
    registratiedatum = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    wachtwoord = db.Column(db.String(255), nullable=False)

class Voertuig(db.Model):
    __tablename__ = 'Voertuigen'
    id = db.Column(db.Integer, primary_key=True)
    nummerplaat = db.Column(db.String(20), unique=True, nullable=False)
    gebruiker_id = db.Column(db.Integer, db.ForeignKey('Gebruikers.id'), nullable=False)
    grootte = db.Column(db.Enum('klein', 'medium', 'groot'), nullable=False)
    is_elektrisch = db.Column(db.Boolean, default=False)
    heeft_handicapkaart = db.Column(db.Boolean, default=False)

class Parkeerplaats(db.Model):
    __tablename__ = 'Parkeerplaatsen'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum('beschikbaar', 'bezet', 'gereserveerd'), nullable=False, default='beschikbaar')
    grootte = db.Column(db.Enum('klein', 'medium', 'groot'), nullable=False)
    locatie = db.Column(db.String(50), nullable=False)
    soort = db.Column(db.Enum('standaard', 'elektrisch', 'handicap'), nullable=False)

class Reservatie(db.Model):
    __tablename__ = 'Reservaties'
    id = db.Column(db.Integer, primary_key=True)
    reservatienummer = db.Column(db.String(50), unique=True, nullable=False)
    gebruiker_id = db.Column(db.Integer, db.ForeignKey('Gebruikers.id'), nullable=False)
    voertuig_id = db.Column(db.Integer, db.ForeignKey('Voertuigen.id'), nullable=False)
    parkeerplaats_id = db.Column(db.Integer, db.ForeignKey('Parkeerplaatsen.id'), nullable=False)
    starttijd = db.Column(db.DateTime, nullable=False)
    eindtijd = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('actief', 'geannuleerd', 'voltooid'), default='actief')
    kosten = db.Column(db.Numeric(10, 2))

# Relatie met de Parkeerplaats
    parkeerplaats = db.relationship('Parkeerplaats', backref='reservaties', lazy=True)

class Betaling(db.Model):
    __tablename__ = 'Betalingen'
    id = db.Column(db.Integer, primary_key=True)
    gebruiker_id = db.Column(db.Integer, db.ForeignKey('Gebruikers.id'), nullable=False)
    reservatie_id = db.Column(db.Integer, db.ForeignKey('Reservaties.id'), nullable=False)
    bedrag = db.Column(db.Numeric(10, 2), nullable=False)
    betaaldatum = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.Enum('betaald', 'mislukt'), default='betaald')

class CameraLog(db.Model):
    __tablename__ = 'CameraLogs'
    id = db.Column(db.Integer, primary_key=True)
    nummerplaat = db.Column(db.String(20), nullable=False)
    tijdstip = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    actie = db.Column(db.Enum('in', 'uit'), nullable=False)

class Statistiek(db.Model):
    __tablename__ = 'Statistieken'
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    totaal_bezet = db.Column(db.Integer, default=0)
    gemiddelde_duur = db.Column(db.Time, default=datetime.time(0, 0, 0))
    totale_inkomsten = db.Column(db.Numeric(10, 2), default=0.00)

# Routes voor API-eindpunten

@app.route('/api/test-database', methods=['GET'])
def test_database():
    try:
        # Voer een eenvoudige query uit
        gebruikers = Gebruiker.query.all()
        if gebruikers:
            return jsonify({
                'message': 'Databaseverbinding is succesvol!',
                'gebruikers_count': len(gebruikers)
            }), 200
        else:
            return jsonify({
                'message': 'Databaseverbinding is succesvol, maar geen gebruikers gevonden.'
            }), 200
    except Exception as e:
        return jsonify({
            'message': 'Fout bij verbinding met de database.',
            'error': str(e)
        }), 500
    
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    naam = data.get('naam')
    email = data.get('email')
    telefoonnummer = data.get('telefoonnummer')
    wachtwoord = data.get('wachtwoord')

    # Wachtwoord hashen
    hashed_password = generate_password_hash(wachtwoord, method='pbkdf2:sha256')

    try:
        # Nieuwe gebruiker aanmaken
        nieuwe_gebruiker = Gebruiker(
            naam=naam,
            email=email,
            telefoonnummer=telefoonnummer,
            wachtwoord=hashed_password
        )
        db.session.add(nieuwe_gebruiker)
        db.session.commit()
        return jsonify({'message': 'Gebruiker succesvol geregistreerd!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Er is een fout opgetreden bij het registreren van de gebruiker.', 'error': str(e)}), 500
    
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Zet je geheime sleutel hier
jwt = JWTManager(app)

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    wachtwoord = data.get('wachtwoord')

    gebruiker = Gebruiker.query.filter_by(email=email).first()
    if gebruiker and check_password_hash(gebruiker.wachtwoord, wachtwoord):
        access_token = create_access_token(identity=gebruiker.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': gebruiker.id,
                'naam': gebruiker.naam,
                'email': gebruiker.email
            }
        }), 200
    return jsonify({'message': 'Ongeldige inloggegevens'}), 401

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    gebruiker = Gebruiker.query.get(user_id)
    if gebruiker:
        return jsonify({
            'naam': gebruiker.naam,
            'email': gebruiker.email,
            'telefoonnummer': gebruiker.telefoonnummer,
            'registratiedatum': gebruiker.registratiedatum
        }), 200
    return jsonify({'message': 'Gebruiker niet gevonden'}), 404

@app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    gebruiker = Gebruiker.query.get(user_id)
    
    if gebruiker:
        return jsonify({
            'message': f"Welkom terug {gebruiker.naam}, Fijn dat je er bent!"
        }), 200
    
    return jsonify({'message': 'Gebruiker niet gevonden'}), 404


@app.route('/api/voertuigen', methods=['POST'])
@jwt_required()
def add_voertuig():
    gebruikerid = get_jwt_identity()  # Haal de gebruiker id op uit de JWT
    data = request.get_json()  # Haal de gegevens uit de body van het verzoek
    nummerplaat = data.get('nummerplaat')
    grootte = data.get('grootte')
    is_elektrisch = data.get('is_elektrisch', False)
    heeft_handicapkaart = data.get('heeft_handicapkaart', False)

    # Voeg het voertuig toe aan de database
    try:
        voertuig = Voertuig(
            nummerplaat=nummerplaat,
            gebruiker_id=gebruikerid,
            grootte=grootte,
            is_elektrisch=is_elektrisch,
            heeft_handicapkaart=heeft_handicapkaart
        )
        db.session.add(voertuig)
        db.session.commit()
        return jsonify({'message': 'Voertuig succesvol toegevoegd!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Fout bij het toevoegen van het voertuig', 'error': str(e)}), 500
    
@app.route('/api/voertuigenzoeken', methods=['GET'])
@jwt_required()
def get_voertuigen():
    gebruikerid = get_jwt_identity()  # Haal het gebruiker id op uit de JWT
    voertuigen = Voertuig.query.filter_by(gebruiker_id=gebruikerid).all() 
    print(voertuigen, gebruikerid) # Filter voertuigen op gebruiker_id
    
    # Als er geen voertuigen zijn gevonden, geef dan een lege lijst terug
    if voertuigen:
        return jsonify([
            {
                'nummerplaat': voertuig.nummerplaat,
                'grootte': voertuig.grootte,
                'is_elektrisch': voertuig.is_elektrisch,
                'heeft_handicapkaart': voertuig.heeft_handicapkaart
            } for voertuig in voertuigen
        ]), 200
    
    return jsonify({'message': 'Geen voertuigen gevonden'}), 404

# Route om een voertuig te bewerken op basis van nummerplaat
@app.route('/api/voertuigen/<string:nummerplaat>', methods=['PUT'])
@jwt_required()
def update_voertuig(nummerplaat):
    gebruikerid = get_jwt_identity()  # Haal de gebruiker id op uit de JWT
    data = request.get_json()  # Haal de gegevens uit de body van het verzoek
    
    # Haal het voertuig op
    voertuig = Voertuig.query.filter_by(nummerplaat=nummerplaat, gebruiker_id=gebruikerid).first()
    if voertuig is None:
        return jsonify({'message': 'Voertuig niet gevonden'}), 404

    # Werk de voertuiggegevens bij
    voertuig.grootte = data.get('grootte', voertuig.grootte)
    voertuig.is_elektrisch = data.get('is_elektrisch', voertuig.is_elektrisch)
    voertuig.heeft_handicapkaart = data.get('heeft_handicapkaart', voertuig.heeft_handicapkaart)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Voertuig succesvol bijgewerkt!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Fout bij het bijwerken van het voertuig', 'error': str(e)}), 500


# Route om een voertuig te verwijderen op basis van nummerplaat
@app.route('/api/voertuigen/<string:nummerplaat>', methods=['DELETE'])
@jwt_required()
def delete_voertuig(nummerplaat):
    gebruiker_id = get_jwt_identity()

    # Zoek het voertuig op basis van nummerplaat
    voertuig = Voertuig.query.filter_by(nummerplaat=nummerplaat, gebruiker_id=gebruiker_id).first()

    if not voertuig:
        return jsonify({'message': 'Voertuig niet gevonden'}), 404

    try:
        db.session.delete(voertuig)
        db.session.commit()
        return jsonify({'message': 'Voertuig succesvol verwijderd!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Fout bij het verwijderen van het voertuig', 'error': str(e)}), 500
@app.route('/api/parkings', methods=['GET'])
def get_parking_spaces():
    parkeerplaatsen = Parkeerplaats.query.all()
    if parkeerplaatsen:
        parking_list = [
            {
                'id': p.id,
                'status': p.status,
                'grootte': p.grootte,
                'locatie': p.locatie,
                'soort': p.soort
            } for p in parkeerplaatsen
        ]
        return jsonify(parking_list), 200
    return jsonify({'message': 'Geen parkeerplaatsen gevonden'}), 404

@app.route('/api/parkings/<int:parking_id>', methods=['GET'])
def get_parking_space_by_id(parking_id):
    parkeerplaats = Parkeerplaats.query.get(parking_id)
    if parkeerplaats:
        return jsonify({
            'id': parkeerplaats.id,
            'status': parkeerplaats.status,
            'grootte': parkeerplaats.grootte,
            'locatie': parkeerplaats.locatie,
            'soort': parkeerplaats.soort  # Voeg de 'soort' hier toe
        }), 200
    return jsonify({'message': 'Parkeerplaats niet gevonden'}), 404


@app.route('/api/parkings/status', methods=['GET'])
def get_parking_status_for_day():
    # Verkrijg de datum van de querystring
    datum_str = request.args.get('datum')  # Bijvoorbeeld: '2025-02-07'
    
    if not datum_str:
        return jsonify({'message': 'Geen datum opgegeven'}), 400
    
    try:
        # Converteer de string naar een datetime object
        datum = datetime.strptime(datum_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Ongeldige datumindeling, gebruik het formaat YYYY-MM-DD'}), 400

    # Haal alle reserveringen op die betrekking hebben op de opgegeven datum
    reservaties = Reservatie.query.filter(
        (Reservatie.starttijd.date() <= datum) & (Reservatie.eindtijd.date() >= datum)
    ).all()

    # Maak een dictionary voor parkeerplaatsen om de status bij te houden
    parkeerplaats_statusen = {p.id: p.status for p in Parkeerplaats.query.all()}

    # Werk de status van de parkeerplaatsen bij op basis van de reserveringen
    for reservatie in reservaties:
        parkeerplaats = Parkeerplaats.query.get(reservatie.parkeerplaats_id)
        if parkeerplaats:
            parkeerplaats_statusen[parkeerplaats.id] = 'bezet'

    # Maak een lijst met parkeerplaatsen en hun status voor de opgegeven datum
    parking_list = [
        {
            'id': p.id,
            'status': parkeerplaats_statusen.get(p.id, 'beschikbaar'),
            'grootte': p.grootte,
            'locatie': p.locatie,
            'soort': p.soort
        } for p in Parkeerplaats.query.all()
    ]
    
    return jsonify(parking_list), 200

@app.route('/api/parkings', methods=['GET'])
def get_parkings():
    datum_str = request.args.get('datum')
    zone = request.args.get('zone')

    if not datum_str:
        return jsonify({'message': 'Geen datum opgegeven'}), 400

    # Zorg ervoor dat de datum in het juiste formaat is
    if len(datum_str) != 10 or datum_str[4] != '-' or datum_str[7] != '-':
        return jsonify({'message': 'Ongeldige datumindeling, gebruik het formaat YYYY-MM-DD'}), 400

    # Haal de reserveringen op voor de opgegeven datum
    reservaties = Reservatie.query.filter(
        (Reservatie.starttijd.ilike(f'{datum_str}%')) & (Reservatie.eindtijd.ilike(f'{datum_str}%'))
    ).all()

    parkeerplaatsen = []
    for reservatie in reservaties:
        parkeerplaatsen.append({
            'id': reservatie.parkeerplaats_id,
            'locatie': reservatie.parkeerplaats.naam,
            'gereserveerd': True,  # Aangegeven dat deze plek gereserveerd is
            'status': 'gereserveerd',
            'reservatie_id': reservatie.id,  # Voeg het reservering ID toe
            'starttijd': reservatie.starttijd,  # Voeg de starttijd van de reservering toe
            'eindtijd': reservatie.eindtijd,  # Voeg de eindtijd van de reservering toe
            'klant': reservatie.klant.naam if reservatie.klant else None,  # Voeg de naam van de klant toe
        })

    # Voeg ongereserveerde parkeerplaatsen toe (optioneel)
    overige_parkeerplaatsen = Parkeerplaats.query.filter(
        Parkeerplaats.zone == zone
    ).all()

    for parkeerplaats in overige_parkeerplaatsen:
        parkeerplaatsen.append({
            'id': parkeerplaats.id,
            'locatie': parkeerplaats.naam,
            'gereserveerd': False,
            'status': 'beschikbaar'
        })

    return jsonify(parkeerplaatsen), 200

@app.route('/api/reservaties/op_datum', methods=['GET'])
@jwt_required()
def get_reservaties_op_datum():
    datum = request.args.get('datum')  # Verwacht een datum in 'YYYY-MM-DD' formaat
    if not datum:
        return jsonify({'message': 'Geen datum opgegeven'}), 400
    
    # Filter op basis van de opgegeven datum
    reservaties = db.session.query(Reservatie, Parkeerplaats).join(Parkeerplaats, Reservatie.parkeerplaats_id == Parkeerplaats.id).filter(
        Reservatie.starttijd.startswith(datum), Reservatie.status == 'actief'
    ).all()
    
    if reservaties:
        reservaties_list = [
            {
                'reservatienummer': r[0].reservatienummer,
                'gebruiker_id': r[0].gebruiker_id,
                'starttijd': r[0].starttijd,
                'eindtijd': r[0].eindtijd,
                'parkeerplaats_id': r[1].id,  # Parkeerplaats ID
                'parkeerplaats_locatie': r[1].locatie  # Parkeerplaats locatie, als je dat wilt
            }
            for r in reservaties
        ]
        return jsonify(reservaties_list), 200
    
    return jsonify({'message': 'Geen actieve reserveringen gevonden voor deze datum'}), 404

@app.route('/api/reservaties/<string:reservatienummer>', methods=['DELETE'])
@jwt_required()
def delete_reservatie(reservatienummer):
    gebruiker_id = get_jwt_identity()

    # Zoek de reservering op basis van reservatienummer en gebruiker_id
    reservatie = Reservatie.query.filter_by(reservatienummer=reservatienummer, gebruiker_id=gebruiker_id).first()

    if not reservatie:
        return jsonify({'message': 'Reservering niet gevonden'}), 404

    try:
        # Verwijder de reservering
        db.session.delete(reservatie)
        db.session.commit()
        return jsonify({'message': 'Reservering succesvol verwijderd!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Fout bij het verwijderen van de reservering', 'error': str(e)}), 500


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

        # Log succesvolle toevoeging
        print(f"Reservering succesvol toegevoegd: {reservatie}")

        return jsonify({'message': 'Reservering succesvol aangemaakt!'}), 201

    except Exception as e:
        db.session.rollback()
        # Log de fout
        print(f"Fout bij het maken van de reservering: {str(e)}")
        return jsonify({'message': 'Fout bij het maken van de reservering', 'error': str(e)}), 500
    
@app.route('/api/reservaties', methods=['GET'])
@jwt_required()
def get_reservaties():
    current_user_id = get_jwt_identity()  # Haal de gebruikers-ID uit het JWT-token
    reservaties = db.session.query(Reservatie, Parkeerplaats).join(Parkeerplaats, Reservatie.parkeerplaats_id == Parkeerplaats.id).filter(
        Reservatie.gebruiker_id == current_user_id, Reservatie.status == 'actief').all()

    if reservaties:
        reservaties_list = [
            {
                'reservatienummer': r[0].reservatienummer,
                'starttijd': r[0].starttijd,
                'eindtijd': r[0].eindtijd,
                'parkeerplaats_id': r[1].id,  # Parkeerplaats ID
                'parkeerplaats_locatie': r[1].locatie  # Parkeerplaats locatie
            }
            for r in reservaties
        ]
        return jsonify(reservaties_list), 200
    return jsonify({'message': 'Geen actieve reserveringen gevonden'}), 404


@app.route('/api/betaling', methods=['POST'])
def add_betaling():
    data = request.get_json()
    gebruiker_id = data.get('gebruiker_id')
    reservatie_id = data.get('reservatie_id')
    bedrag = data.get('bedrag')

    try:
        betaling = Betaling(
            gebruiker_id=gebruiker_id,
            reservatie_id=reservatie_id,
            bedrag=bedrag
        )
        db.session.add(betaling)
        db.session.commit()
        return jsonify({'message': 'Betaling succesvol geregistreerd!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Fout bij het verwerken van de betaling', 'error': str(e)}), 500
    
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your-email@example.com'
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@example.com', 'your-email-password')
        server.sendmail('your-email@example.com', to_email, msg.as_string())

@app.route('/api/reservering/bestätigung', methods=['POST'])
def bevestiging_email():
    data = request.get_json()
    to_email = data.get('email')
    subject = "Bevestiging van reservering"
    body = "Uw reservering is succesvol bevestigd!"

    try:
        send_email(to_email, subject, body)
        return jsonify({'message': 'Bevestigingsmail succesvol verzonden!'}), 200
    except Exception as e:
        return jsonify({'message': 'Fout bij het verzenden van de bevestigingsmail', 'error': str(e)}), 500
    
@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    gebruiker = Gebruiker.query.get(user_id)
    if gebruiker:
        return jsonify({
            'id': gebruiker.id,
            'naam': gebruiker.naam,
            'email': gebruiker.email
        }), 200
    return jsonify({'message': 'Gebruiker niet gevonden'}), 404  

# Start de server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Zorgt ervoor dat tabellen bestaan
    app.run(debug=True)
