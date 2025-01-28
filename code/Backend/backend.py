from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import smtplib
from email.mime.text import MIMEText
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)
CORS(app)

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
        # Maak een JWT-token voor de ingelogde gebruiker
        access_token = create_access_token(identity=gebruiker.id)
        return jsonify({'access_token': access_token}), 200
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

@app.route('/api/voertuigen', methods=['POST'])
def add_voertuig():
    data = request.get_json()
    nummerplaat = data.get('nummerplaat')
    gebruiker_id = data.get('gebruiker_id')
    grootte = data.get('grootte')
    is_elektrisch = data.get('is_elektrisch', False)
    heeft_handicapkaart = data.get('heeft_handicapkaart', False)

    try:
        voertuig = Voertuig(
            nummerplaat=nummerplaat,
            gebruiker_id=gebruiker_id,
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
    
@app.route('/api/voertuigen/<int:gebruiker_id>', methods=['GET'])
def get_voertuigen(gebruiker_id):
    voertuigen = Voertuig.query.filter_by(gebruiker_id=gebruiker_id).all()
    if voertuigen:
        voertuigen_list = [
            {'nummerplaat': v.nummerplaat, 'grootte': v.grootte, 'is_elektrisch': v.is_elektrisch, 'heeft_handicapkaart': v.heeft_handicapkaart}
            for v in voertuigen
        ]
        return jsonify(voertuigen_list), 200
    return jsonify({'message': 'Geen voertuigen gevonden voor deze gebruiker'}), 404

@app.route('/api/reservaties', methods=['POST'])
def create_reservatie():
    data = request.get_json()
    gebruiker_id = data.get('gebruiker_id')
    voertuig_id = data.get('voertuig_id')
    parkeerplaats_id = data.get('parkeerplaats_id')
    starttijd = data.get('starttijd')
    eindtijd = data.get('eindtijd')

    try:
        # Maak een nieuwe reservering
        reservatie = Reservatie(
            gebruiker_id=gebruiker_id,
            voertuig_id=voertuig_id,
            parkeerplaats_id=parkeerplaats_id,
            starttijd=starttijd,
            eindtijd=eindtijd
        )
        db.session.add(reservatie)
        db.session.commit()
        return jsonify({'message': 'Reservering succesvol aangemaakt!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Fout bij het maken van de reservering', 'error': str(e)}), 500
    
@app.route('/api/reservaties', methods=['GET'])
@jwt_required()
def get_reservaties():
    current_user_id = get_jwt_identity()  # Haal de gebruikers-ID uit het JWT-token
    reservaties = Reservatie.query.filter_by(gebruiker_id=current_user_id, status='actief').all()
    if reservaties:
        reservaties_list = [
            {'reservatienummer': r.reservatienummer, 'starttijd': r.starttijd, 'eindtijd': r.eindtijd}
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
    

# Start de server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Zorgt ervoor dat tabellen bestaan
    app.run(debug=True)
