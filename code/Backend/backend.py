from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import smtplib
from email.mime.text import MIMEText
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import uuid
import datetime
from dateutil import parser
import pytz
from werkzeug.exceptions import BadRequest
from sqlalchemy.sql import func
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytesseract
import numpy as np
import re
import io
from PIL import Image
import easyocr

#!!!
#school wifi laat geen mails versturen enkel op 4g of mogelijks andere wifi wel 
#!!!

kosten_per_uur = 5.00  # Kosten per uur (standaardwaarde)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True, )

# Database configuratie
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/parkeergarage_beheer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # Zet de debugmodus aan

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

class Parkeerregistratie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kenteken = db.Column(db.String(20), unique=True, nullable=False)
    ingangsdatum = db.Column(db.DateTime, nullable=False)
    uitgangsdatum = db.Column(db.DateTime)
    parkeerplaats = db.Column(db.String(100))

# Routes voor API-eindpunten

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

reader = easyocr.Reader(['en'])  # 'en' is voor Engels, je kunt meer talen toevoegen zoals 'nl', 'fr', etc.

# Reguliere expressies voor nummerplaten, met spaties, streepjes, en speciale tekens toegestaan
BELGIUM_PLATE_REGEX = r"\d{1}\s*-?\s*[A-Za-z]{3}\s*-?\s*\d{3}"   # België nummerplaat (oude formaat)
BELGIUM_PLATE_REGEX_V2 = r"\d{1}\s*-?\s*[A-Za-z]{2}\s*-?\s*\d{4}"  # Alternatief Belgisch formaat voor oldtimers

NETHERLANDS_PLATE_REGEX = r"[A-Za-z]{2}\s*-?\s*\d{2}\s*-?\s*\d{2}"  # Nederland nummerplaat (format 1)
NETHERLANDS_PLATE_REGEX2 = r"\d{2}\s*-?\s*\d{2}\s*-?\s*[A-Za-z]{2}"  # Nederland nummerplaat (format 2)
NETHERLANDS_PLATE_REGEX3 = r"\d{2}\s*-?\s*[A-Za-z]{2}\s*-?\s*\d{2}"  # Nederland nummerplaat (format 3)
NETHERLANDS_PLATE_REGEX21 = r"[A-Za-z]\s*\d{3}\s*[A-Za-z]{2}"        # A 123 BC
NETHERLANDS_PLATE_REGEX22 = r"[A-Za-z]{2}\s*\d{3}\s*[A-Za-z]"        # AB 123 C

FRANCE_PLATE_REGEX = r"[A-Za-z]{2}\s*-?\s*\d{3}\s*-?\s*[A-Za-z]{2}"  # Franse nummerplaat met spaties en streepjes
FRANCE_PLATE_REGEX2 = r"\d{3}\s*-?\s*[A-Za-z]{3}\s*-?\s*\d{2}"       # Frankrijk nummerplaat (format 2)

GERMANY_PLATE_REGEX = r"[A-Za-z]{1,3}-\d{1,4}"                       # Duitsland nummerplaat (format 1)
GERMANY_PLATE_REGEX2 = r"[A-Za-z]{1,3}-[A-Za-z]{1,2} \d{1,4}"        # Duitsland nummerplaat (format 2)

# Functie om ongewenste tekens (zoals #, ., -, etc.) te verwijderen
def clean_text(text):
    # Verwijder alle speciale tekens, inclusief punten en streepjes
    cleaned_text = re.sub(r'[^\w\s]', '', text)  # Behoud alleen letters, cijfers en spaties
    return cleaned_text

# Functie om verwarrende tekens te vervangen (zoals 0 -> O, 4 -> A, Q -> 0)
def replace_confusing_chars(text):
    # Vervang verwarrende cijfers door letters alleen als het echt nodig is
    text = text.replace('0', 'O')  # Vervang 0 door O
    text = text.replace('4', 'A')  # Vervang 4 door A
    text = text.replace('Q', '0')  # Vervang Q door 0
    text = text.replace('L', '1')  # Vervang L door 1
    return text

# Functie om nummerplaat te vinden
def extract_license_plate(text):
    # Eerst de tekst schoonmaken en controleren
    cleaned_text = clean_text(text)

    # Controleer of de tekst geen begin cijfer heeft en voeg 1 toe als dat het geval is
    if not re.match(r'\d', cleaned_text):  # Als de tekst niet begint met een cijfer
        cleaned_text = '1 ' + cleaned_text  # Voeg standaard een '1' voor de nummerplaat

    # Eerst proberen voor Belgische nummerplaten
    if re.search(BELGIUM_PLATE_REGEX, cleaned_text):
        return re.search(BELGIUM_PLATE_REGEX, cleaned_text).group(0)

    if re.search(BELGIUM_PLATE_REGEX_V2, cleaned_text):
        return re.search(BELGIUM_PLATE_REGEX_V2, cleaned_text).group(0)

    # Nederlandse nummerplaten
    if re.search(NETHERLANDS_PLATE_REGEX, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX, cleaned_text).group(0)

    if re.search(NETHERLANDS_PLATE_REGEX2, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX2, cleaned_text).group(0)

    if re.search(NETHERLANDS_PLATE_REGEX3, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX3, cleaned_text).group(0)
    
    if re.search(NETHERLANDS_PLATE_REGEX21, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX21, cleaned_text).group(0)
    
    # Nederlands (AB 123 C)
    if re.search(NETHERLANDS_PLATE_REGEX22, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX22, cleaned_text).group(0)

    # Franse nummerplaten
    if re.search(FRANCE_PLATE_REGEX, cleaned_text):
        return re.search(FRANCE_PLATE_REGEX, cleaned_text).group(0)

    if re.search(FRANCE_PLATE_REGEX2, cleaned_text):
        return re.search(FRANCE_PLATE_REGEX2, cleaned_text).group(0)

    # Duitse nummerplaten
    if re.search(GERMANY_PLATE_REGEX, cleaned_text):
        return re.search(GERMANY_PLATE_REGEX, cleaned_text).group(0)

    if re.search(GERMANY_PLATE_REGEX2, cleaned_text):
        return re.search(GERMANY_PLATE_REGEX2, cleaned_text).group(0)
    
    # Stap 3: Als de eerste poging geen resultaat oplevert, probeer verwisselingen
    cleaned_text = replace_confusing_chars(cleaned_text)

    # Herhaal de checks na vervangingen
    if re.search(BELGIUM_PLATE_REGEX, cleaned_text):
        return re.search(BELGIUM_PLATE_REGEX, cleaned_text).group(0)

    if re.search(BELGIUM_PLATE_REGEX_V2, cleaned_text):
        return re.search(BELGIUM_PLATE_REGEX_V2, cleaned_text).group(0)

    if re.search(NETHERLANDS_PLATE_REGEX, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX, cleaned_text).group(0)

    if re.search(NETHERLANDS_PLATE_REGEX2, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX2, cleaned_text).group(0)

    if re.search(NETHERLANDS_PLATE_REGEX3, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX3, cleaned_text).group(0)
    
    if re.search(NETHERLANDS_PLATE_REGEX21, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX21, cleaned_text).group(0)
    
    if re.search(NETHERLANDS_PLATE_REGEX22, cleaned_text):
        return re.search(NETHERLANDS_PLATE_REGEX22, cleaned_text).group(0)

    if re.search(FRANCE_PLATE_REGEX, cleaned_text):
        return re.search(FRANCE_PLATE_REGEX, cleaned_text).group(0)

    if re.search(FRANCE_PLATE_REGEX2, cleaned_text):
        return re.search(FRANCE_PLATE_REGEX2, cleaned_text).group(0)

    if re.search(GERMANY_PLATE_REGEX, cleaned_text):
        return re.search(GERMANY_PLATE_REGEX, cleaned_text).group(0)

    if re.search(GERMANY_PLATE_REGEX2, cleaned_text):
        return re.search(GERMANY_PLATE_REGEX2, cleaned_text).group(0)
    
    return None

# Functie om nummerplaat te formatteren
def format_license_plate(license_plate):
    license_plate = license_plate.upper()

    # Belgische nummerplaat
    if re.match(r"\d\s*[A-Za-z]{3}\s*\d{3}", license_plate):
        license_plate = re.sub(r"(\d)\s*([A-Za-z]{3})\s*(\d{3})", r"\1 \2 \3", license_plate)
    
    # Nederlandse nummerplaat (format 1: 22 DA 89)
    elif re.match(r"\d{2}\s*[A-Za-z]{2}\s*\d{2}", license_plate):
        license_plate = re.sub(r"(\d{2})([A-Za-z]{2})(\d{2})", r"\1 \2 \3", license_plate)

    # Nederlandse nummerplaat (format 2: 12 34 AB)
    elif re.match(r"\d{2}\s*-?\s*\d{2}\s*-?\s*[A-Za-z]{2}", license_plate):
        license_plate = re.sub(r"(\d{2})([A-Za-z]{2})(\d{2})", r"\1 \2 \3", license_plate)

    # Nederlandse nummerplaat (A 123 BC)
    elif re.match(r"[A-Za-z]\s*\d{3}\s*[A-Za-z]{2}", license_plate):
        license_plate = re.sub(r"([A-Za-z])\s*(\d{3})\s*([A-Za-z]{2})", r"\1 \2 \3", license_plate)

    # Nederlandse nummerplaat (ab 123 c)
    elif re.match(r"[A-Za-z]{2}\s*\d{3}\s*[A-Za-z]", license_plate):
        license_plate = re.sub(r"([A-Za-z]{2})\s*(\d{3})\s*([A-Za-z])", r"\1 \2 \3", license_plate)


    # Franse nummerplaat
    elif re.match(r"[A-Za-z]{2}\s*\d{3}\s*[A-Za-z]{2}", license_plate):
        license_plate = re.sub(r"([A-Za-z]{2})(\d{3})([A-Za-z]{2})", r"\1 \2 \3", license_plate)
    
    # Duitse nummerplaat
    elif re.match(r"[A-Za-z]{1,3}-\d{1,4}", license_plate):
        license_plate = re.sub(r"([A-Za-z]{1,3})-(\d{1,4})", r"\1-\2", license_plate)

    # Verwijder dubbele spaties
    license_plate = re.sub(r'\s+', ' ', license_plate)
    
    return license_plate


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    
    try:
        # Open de afbeelding met Pillow
        image = Image.open(io.BytesIO(image_file.read()))
        
        # Converteer de afbeelding naar een numpy array
        image_np = np.array(image)
        
        # Gebruik EasyOCR om tekst uit de afbeelding te halen
        result = reader.readtext(image_np)
        
        # Verkrijg de tekst van de OCR-resultaten
        text = ' '.join([r[1] for r in result])  # r[1] is de herkende tekst
        #print('herkende text:', text)  # Debugging: print de herkende tekst

        license_plate = extract_license_plate(text)
        #print("Gevonden nummerplaat:", license_plate)  # Debugging: print de gevonden nummerplaat

        if license_plate:
            # Formatteer de nummerplaat
            formatted_license_plate = format_license_plate(license_plate)
            #print("Geformatteerde nummerplaat:", formatted_license_plate)  # Debugging: print de geformatteerde nummerplaat

            # Retourneer de geformatteerde nummerplaat als JSON response
            return jsonify({'nummerplaat': formatted_license_plate})
        else:
            return jsonify({'error': 'No license plate found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/verwijder_reservering', methods=['POST'])
def verwijder_reservering():
    data = request.get_json()
    nummerplaat = data.get('nummerplaat')

    # Zoek de reservering op basis van het kenteken
    registratie = Parkeerregistratie.query.filter_by(kenteken=nummerplaat).first()

    if not registratie:
        return {"message": "Reservering niet gevonden"}, 404

    # Verwijder de reservering
    db.session.delete(registratie)
    db.session.commit()

    return {"message": "Reservering succesvol verwijderd"}, 200

# Functie om tijdsduur te berekenen
def bereken_tijdsduur(ingangsdatum, uitgangsdatum):
    duur = uitgangsdatum - ingangsdatum
    uren = duur.total_seconds() / 3600  # Zet om naar uren
    return round(uren, 2)

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

@app.route('/check_numberplate', methods=['POST'])
def check_numberplate():
    nummerplaat = request.json.get('nummerplaat')
    
    # Zoek het voertuig op basis van de nummerplaat
    voertuig = Voertuig.query.filter_by(nummerplaat=nummerplaat).first()
    
    if voertuig:
        # Zoek de bijbehorende reservering via voertuig_id en filter op de huidige datum
        vandaag = date.today()
        reservering = Reservatie.query.filter(
            Reservatie.voertuig_id == voertuig.id,
            func.date(Reservatie.starttijd) == vandaag
        ).first()
        
        if reservering:
            # Zoek de parkeerplaats op basis van het parkeerplaats_id in de reservering
            parkeerplaats = Parkeerplaats.query.filter_by(id=reservering.parkeerplaats_id).first()
            
            if parkeerplaats:
                # Verkrijg de gebruiker en zijn e-mailadres via de reservering
                gebruiker = Gebruiker.query.filter_by(id=reservering.gebruiker_id).first()
                if gebruiker:
                    email = gebruiker.email  # Haal het e-mailadres op van de gebruiker
                else:
                    email = None  # Indien geen gebruiker gevonden, zet e-mail naar None

                # Bouw de response met de gegevens
                response = {
                    'status': 'found',
                    'nummerplaat': nummerplaat,
                    'reservatienummer': reservering.reservatienummer,
                    'starttijd': reservering.starttijd.isoformat(),
                    'eindtijd': reservering.eindtijd.isoformat(),
                    'status': reservering.status,
                    'locatie': parkeerplaats.locatie  # Voeg locatie van de parkeerplaats toe
                }

                # Verzend de e-mail met de benodigde gegevens
                send_confirmation_email(reservering, nummerplaat, parkeerplaats.locatie, email)  # E-mail functie apart aanroepen
                
                return jsonify(response)
            else:
                return jsonify({'status': 'not_found', 'message': 'Parkeerplaats niet gevonden voor deze reservering'})
        else:
            return jsonify({'status': 'not_found', 'message': 'Geen reservering gevonden voor vandaag'})
    else:
        return jsonify({'status': 'not_found', 'message': 'Voertuig niet gevonden met deze nummerplaat'})

def send_confirmation_email(reservering, nummerplaat, locatie, email):
    print('In de send_confirmation_email functie')

    # E-mailgegevens
    sender_email = "bramswinnen1@gmail.com"
    receiver_email = email  # Het e-mailadres van de klant
    subject = f"Toegang verleend bij Smart Parking - Reservering {reservering.reservatienummer}"

    # HTML e-mailinhoud
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #2c3e50;">Toegang verleend bij Smart Parking</h2>
            <p>Beste klant,</p>
            <p>Je bent zojuist <strong>binnengereden bij Smart Parking</strong>. Jouw nummerplaat <strong>{nummerplaat}</strong> is herkend en gekoppeld aan een bestaande reservering.</p>
            <h3>Reserveringsgegevens:</h3>
            <ul>
                <li><strong>Reserveringsnummer:</strong> {reservering.reservatienummer}</li>
                <li><strong>Datum:</strong> {date.today()}</li>
                <li><strong>Starttijd:</strong> {reservering.starttijd}</li>
                <li><strong>Eindtijd:</strong> {reservering.eindtijd}</li>
                <li><strong>Parkeerplaatslocatie:</strong> {locatie}</li>
            </ul>
            <p>Bedankt voor je bezoek aan <strong>Smart Parking</strong>. Wij wensen je een prettige dag!</p>
            <br>
            <p style="font-size: 12px; color: #7f8c8d;">Met vriendelijke groet,<br>
            <strong>Het Smart Parking Team</strong></p>
        </div>
    </body>
    </html>
    """

    # Maak de e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))  # Alleen HTML-versie bijvoegen

    # Verstuur de e-mail via Gmail SMTP-server
    try:
        print('Verbinding maken met de SMTP-server...')
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Zet de debugmodus aan om te loggen
            server.starttls()  # Start TLS-beveiliging
            server.login(sender_email, 'mgoxlowhwjpudbdl')  # Gebruik je app-specifieke wachtwoord
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f'E-mail succesvol verzonden naar {receiver_email}')
    
    except smtplib.SMTPException as e:
        print(f"SMTP fout: {e}")
    except Exception as e:
        print(f"Onverwachte fout: {e}")

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

@app.route('/check_numberplate_uit', methods=['POST'])
def check_numberplate_uit():
    nummerplaat = request.json.get('nummerplaat')
    print("juiste functie lets go")
    
    # Zoek het voertuig op basis van de nummerplaat
    voertuig = Voertuig.query.filter_by(nummerplaat=nummerplaat).first()
    
    if voertuig:
        # Zoek de bijbehorende reservering via voertuig_id en filter op de huidige datum
        vandaag = date.today()
        reservering = Reservatie.query.filter(
            Reservatie.voertuig_id == voertuig.id,
            func.date(Reservatie.starttijd) == vandaag
        ).first()
        
        if reservering:
            # Zoek de parkeerplaats op basis van het parkeerplaats_id in de reservering
            parkeerplaats = Parkeerplaats.query.filter_by(id=reservering.parkeerplaats_id).first()
            
            if parkeerplaats:
                # Verkrijg de gebruiker en zijn e-mailadres via de reservering
                gebruiker = Gebruiker.query.filter_by(id=reservering.gebruiker_id).first()
                if gebruiker:
                    email = gebruiker.email  # Haal het e-mailadres op van de gebruiker
                else:
                    email = None  # Indien geen gebruiker gevonden, zet e-mail naar None

                # Bouw de response met de gegevens
                response = {
                    'status': 'found',
                    'nummerplaat': nummerplaat,
                    'reservatienummer': reservering.reservatienummer,
                    'starttijd': reservering.starttijd.isoformat(),
                    'eindtijd': reservering.eindtijd.isoformat(),
                    'status': reservering.status,
                    'locatie': parkeerplaats.locatie  # Voeg locatie van de parkeerplaats toe
                }

                # Verzend de e-mail met de benodigde gegevens
                send_exit_confirmation_email(reservering, nummerplaat, parkeerplaats.locatie, email)  # E-mail functie apart aanroepen
                
                return jsonify(response)
            else:
                return jsonify({'status': 'not_found', 'message': 'Parkeerplaats niet gevonden voor deze reservering'})
        else:
            return jsonify({'status': 'not_found', 'message': 'Geen reservering gevonden voor vandaag'})
    else:
        return jsonify({'status': 'not_found', 'message': 'Voertuig niet gevonden met deze nummerplaat'})
    
def send_exit_confirmation_email(reservering, nummerplaat, locatie, email):
    print('In de send_exit_confirmation_email functie')

    # E-mailgegevens
    sender_email = "bramswinnen1@gmail.com"
    receiver_email = email  # Het e-mailadres van de klant
    subject = f"Uitgangsbevestiging - Smart Parking - Reservering {reservering.reservatienummer}"

    # HTML e-mailinhoud
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #2c3e50;">Je hebt Smart Parking verlaten</h2>
            <p>Beste klant,</p>
            <p>Je bent zojuist <strong>uitgereden bij Smart Parking</strong>. Jouw nummerplaat <strong>{nummerplaat}</strong> is herkend en afgemeld bij de reservering.</p>
            <h3>Reserveringsgegevens:</h3>
            <ul>
                <li><strong>Reserveringsnummer:</strong> {reservering.reservatienummer}</li>
                <li><strong>Datum:</strong> {date.today()}</li>
                <li><strong>Starttijd:</strong> {reservering.starttijd}</li>
                <li><strong>Eindtijd:</strong> {reservering.eindtijd}</li>
                <li><strong>Parkeerplaatslocatie:</strong> {locatie}</li>
            </ul>
            <p>Bedankt voor je bezoek aan <strong>Smart Parking</strong>. Wij hopen je snel weer te zien!</p>
            <br>
            <p style="font-size: 12px; color: #7f8c8d;">Met vriendelijke groet,<br>
            <strong>Het Smart Parking Team</strong></p>
        </div>
    </body>
    </html>
    """

    # Maak de e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))  # Alleen HTML-versie bijvoegen

    # Verstuur de e-mail via Gmail SMTP-server
    try:
        print('Verbinding maken met de SMTP-server...')
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Zet de debugmodus aan om te loggen
            server.starttls()  # Start TLS-beveiliging
            server.login(sender_email, 'mgoxlowhwjpudbdl')  # Gebruik je app-specifieke wachtwoord
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f'E-mail succesvol verzonden naar {receiver_email}')
    
    except smtplib.SMTPException as e:
        print(f"SMTP fout: {e}")
    except Exception as e:
        print(f"Onverwachte fout: {e}")






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

def update_reservaties():
    with app.app_context():  # Zorg ervoor dat de context correct geladen is
        now = datetime.datetime.now()  # Gebruik datetime.datetime voor de tijd
        afgelopen_reservaties = Reservatie.query.filter(Reservatie.eindtijd < now, Reservatie.status == 'actief').all()

        if not afgelopen_reservaties:
            print("Geen actieve reserveringen gevonden die verlopen zijn.")
        
        for reservatie in afgelopen_reservaties:
            print(f"Voordat we de status bijwerken: Reservatie ID {reservatie.id} - Status: {reservatie.status}")
            reservatie.status = 'verlopen'  # Status veranderen naar 'verlopen'
            print(f"Na bijwerken van de status: Reservatie ID {reservatie.id} - Nieuwe Status: {reservatie.status}")
        
        db.session.commit()  # Zorg ervoor dat de wijzigingen worden opgeslagen in de database
        print(f'{len(afgelopen_reservaties)} reserveringen bijgewerkt naar "verlopen".')

@app.route('/update_reservaties', methods=['POST'])
def update_reservaties_route():
    update_reservaties()
    return jsonify({'message': 'Reserveringen bijgewerkt'}), 200

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
    
def send_reservation_email(reservering, nummerplaat, locatie, email):
    print('In de send_reservation_email functie')

    # E-mailgegevens
    sender_email = "bramswinnen1@gmail.com"
    receiver_email = email  # Het e-mailadres van de klant
    subject = f"Bevestiging van je reservering - Smart Parking"

    # HTML e-mailinhoud
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #2c3e50;">Bevestiging van je reservering</h2>
            <p>Beste klant,</p>
            <p>Je hebt succesvol een <strong>parkeerplaats gereserveerd</strong> bij Smart Parking.</p>
            <h3>Reserveringsgegevens:</h3>
            <ul>
                <li><strong>Reserveringsnummer:</strong> {reservering.reservatienummer}</li>
                <li><strong>Datum:</strong> {date.today()}</li>
                <li><strong>Starttijd:</strong> {reservering.starttijd}</li>
                <li><strong>Eindtijd:</strong> {reservering.eindtijd}</li>
                <li><strong>Parkeerplaatslocatie:</strong> {locatie}</li>
                <li><strong>Nummerplaat:</strong> {nummerplaat}</li>
                <li><strong>Kosten:</strong> €{reservering.kosten:.2f}</li>
            </ul>
            <p>Bedankt voor je reservering bij <strong>Smart Parking</strong>. We kijken uit naar je bezoek!</p>
            <br>
            <p style="font-size: 12px; color: #7f8c8d;">Met vriendelijke groet,<br>
            <strong>Het Smart Parking Team</strong></p>
        </div>
    </body>
    </html>
    """

    # Maak de e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))  # Alleen HTML-versie bijvoegen

    # Verstuur de e-mail via Gmail SMTP-server
    try:
        print('Verbinding maken met de SMTP-server...')
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Zet de debugmodus aan om te loggen
            server.starttls()  # Start TLS-beveiliging
            server.login(sender_email, 'mgoxlowhwjpudbdl')  # Gebruik je app-specifieke wachtwoord
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f'E-mail succesvol verzonden naar {receiver_email}')
    
    except smtplib.SMTPException as e:
        print(f"SMTP fout: {e}")
    except Exception as e:
        print(f"Onverwachte fout: {e}")
    
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

#niet in gebruik mogelijks nog wel
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

gecontroleerde_parkeringen = []

@app.route('/get_available_parking', methods=['POST'])
def get_available_parking():
    grootte = request.json.get('grootte')
    soort = request.json.get('soort')

    # Verkrijg de huidige datum
    vandaag = datetime.datetime.now().date()

    # Zoek beschikbare parkeerplaatsen op basis van grootte en soort
    beschikbare_parkeringen = Parkeerplaats.query.filter_by(status='beschikbaar', grootte=grootte, soort=soort).all()

    # Als er parkeerplaatsen beschikbaar zijn, controleren we of ze al zijn gereserveerd
    if beschikbare_parkeringen:
        # Draai de lijst om zodat we van achter naar voren zoeken
        beschikbare_parkeringen.reverse()

        for parkeerplaats in beschikbare_parkeringen:
            # Check of deze parkeerplaats al in de lijst van gecontroleerde parkeerplaatsen staat
            if parkeerplaats.id in gecontroleerde_parkeringen:
                continue  # Als deze al gecontroleerd is, zoek dan verder

            # Voeg deze parkeerplaats toe aan de lijst van gecontroleerde parkeerplaatsen
            gecontroleerde_parkeringen.append(parkeerplaats.id)

            # Controleer of de parkeerplaats al gereserveerd is voor de huidige dag
            reserveringen_op_dag = Reservatie.query.filter(
                Reservatie.parkeerplaats_id == parkeerplaats.id,
                func.date(Reservatie.starttijd) <= vandaag,  # Gebruik de func.date om de datum te vergelijken
                func.date(Reservatie.eindtijd) >= vandaag,   # Gebruik de func.date om de datum te vergelijken
                Reservatie.status != 'geannuleerd'          # Status mag niet geannuleerd zijn
            ).all()

            # Als er geen reserveringen voor de parkeerplaats op de huidige dag zijn, geef deze dan terug
            if not reserveringen_op_dag:
                return jsonify({
                    'parkering': {
                        'id': parkeerplaats.id,
                        'locatie': parkeerplaats.locatie,
                        'grootte': parkeerplaats.grootte,
                        'soort': parkeerplaats.soort
                    }
                })

        # Als we hier komen, betekent het dat alle parkeerplaatsen zijn gereserveerd
        return jsonify({'message': 'Geen parkeerplaats beschikbaar'}), 404

    else:
        return jsonify({'message': 'Geen parkeerplaats beschikbaar'}), 404
    
gereserveerde_parkeerplaatsen = []

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
        app.logger.info(f"Ontvangen data: {request.json}")

        # Controleer of alle vereiste gegevens aanwezig zijn
        if not nummerplaat or not eindtijd or not parkeerplaats_id or not grootte or not soort:
            raise BadRequest("Niet alle benodigde gegevens zijn ontvangen")

        # Zoek de parkeerplaats op basis van parkeerplaats_id
        parkeerplaats = Parkeerplaats.query.filter_by(id=parkeerplaats_id).first()

        if parkeerplaats is None:
            raise BadRequest(f'Parkeerplaats met ID {parkeerplaats_id} bestaat niet.')

        # Controleer of de parkeerplaats al gereserveerd is in de tijdelijke lijst
        if parkeerplaats_id in gereserveerde_parkeerplaatsen:
            raise BadRequest("Deze parkeerplaats is al tijdelijk gereserveerd.")

        # Voeg de parkeerplaats toe aan de lijst van gereserveerde parkeerplaatsen
        gereserveerde_parkeerplaatsen.append(parkeerplaats_id)
        app.logger.info(f"Gereserveerde parkeerplaatsen: {gereserveerde_parkeerplaatsen}")

        # Gebruik dateutil.parser om de eindtijd om te zetten naar datetime (aware datetime)
        eindtijd = parser.isoparse(eindtijd)

        # Zet de starttijd naar de huidige UTC tijd, als een aware datetime
        starttijd = datetime.datetime.now(pytz.utc)

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
            gebruiker_id=gebruiker_id,
            voertuig_id=10000,  # Dit kan je aanpassen naar het juiste voertuig_id
            parkeerplaats_id=parkeerplaats.id,
            starttijd=starttijd,
            eindtijd=eindtijd,
            kosten=kosten
        )

        # Voeg de reservering toe aan de database
        db.session.add(reservatie)
        db.session.commit()

        # Log het succes
        app.logger.info(f"Reservering succesvol toegevoegd: {reservatie}")

        return jsonify({'message': 'Reservering succesvol aangemaakt!', 'reservatienummer': reservatienummer}), 201

    except Exception as e:
        # Verwijder de parkeerplaats uit de lijst als er een fout optreedt
        if parkeerplaats_id in gereserveerde_parkeerplaatsen:
            gereserveerde_parkeerplaatsen.remove(parkeerplaats_id)

        app.logger.error(f"Er is een fout opgetreden: {str(e)}")
        return jsonify({'message': 'Er is een fout opgetreden bij het aanmaken van de reservering.'}), 500


@app.route('/api/reserveringen', methods=['GET'])
def get_reserveringen():
    reserveringen = Reservatie.query.all()
    return jsonify([{
        'id': r.id,
        'reservatienummer': r.reservatienummer,
        'starttijd': r.starttijd.strftime('%Y-%m-%d %H:%M'),
        'eindtijd': r.eindtijd.strftime('%Y-%m-%d %H:%M'),
        'status': r.status
    } for r in reserveringen])

@app.route('/api/parkeerplaatsen', methods=['GET'])
def get_parkeerplaatsen():
    parkeerplaatsen = Parkeerplaats.query.all()
    return jsonify([{
        'id': p.id,
        'status': p.status,
        'locatie': p.locatie,
        'soort': p.soort
    } for p in parkeerplaatsen])

@app.route('/api/statistieken', methods=['GET'])
def get_statistieken():
    today = datetime.date.today()
    
    statistiek = Statistiek.query.filter_by(datum=today).first()

    if not statistiek:
        return jsonify({
            "datum": str(today),
            "totaal_bezet": 0,
            "gemiddelde_duur": "00:00:00",
            "totale_inkomsten": 0.00
        })
    
    return jsonify({
        "datum": str(statistiek.datum),
        "totaal_bezet": statistiek.totaal_bezet,
        "gemiddelde_duur": str(statistiek.gemiddelde_duur),
        "totale_inkomsten": float(statistiek.totale_inkomsten)
    })

# API endpoint: Statistieken updaten
@app.route('/api/update_statistieken', methods=['POST'])
def update_statistieken():
    today = datetime.date.today()

    # Bereken totaal aantal bezette parkeerplaatsen
    now = datetime.datetime.now()
    totaal_bezet = Reservatie.query.filter(
        Reservatie.status == 'actief',
        Reservatie.starttijd <= now,
        Reservatie.eindtijd >= now
    ).count()

    # Bereken gemiddelde parkeertijd
    # We trekken het verschil af tussen 'eindtijd' en 'starttijd' en berekenen daarna het gemiddelde
    avg_duur_result = db.session.query(func.avg(Reservatie.eindtijd - Reservatie.starttijd)).scalar()

    # Controleer of avg_duur_result een geldige waarde is
    if avg_duur_result is not None:
        # Het resultaat is een decimal, dus we moeten het omzetten naar een timedelta
        total_seconds = float(avg_duur_result)  # Omzetten naar float om seconden te krijgen
        
        # Bereken de uren, minuten en seconden, waarbij we de dagen omrekenen naar uren
        total_days = int(total_seconds // (24 * 3600))  # Aantal dagen
        remaining_seconds = total_seconds % (24 * 3600)  # De resterende seconden binnen de dag
        hours = int(remaining_seconds // 3600)
        minutes = int((remaining_seconds % 3600) // 60)
        seconds = int(remaining_seconds % 60)

        # Voeg de dagen (omgezet naar uren) toe aan de uren
        total_hours = total_days * 24 + hours

        # Stel de gemiddelde duur in als een tijd object in het formaat uren:minuten:seconden
        gemiddelde_duur = str(datetime.timedelta(hours=total_hours, minutes=minutes, seconds=seconds))

    else:
        gemiddelde_duur = datetime.time(0, 0, 0)

    # Bereken totale inkomsten
    totale_inkomsten = db.session.query(func.sum(Reservatie.kosten)).scalar()
    totale_inkomsten = float(totale_inkomsten) if totale_inkomsten else 0.00

    # Voeg of update statistieken
    statistiek = Statistiek.query.filter_by(datum=today).first()
    if statistiek:
        statistiek.totaal_bezet = totaal_bezet
        statistiek.gemiddelde_duur = gemiddelde_duur
        statistiek.totale_inkomsten = totale_inkomsten
    else:
        nieuwe_statistiek = Statistiek(
            datum=today,
            totaal_bezet=totaal_bezet,
            gemiddelde_duur=gemiddelde_duur,
            totale_inkomsten=totale_inkomsten
        )
        db.session.add(nieuwe_statistiek)

    db.session.commit()

    return jsonify({"message": "Statistieken bijgewerkt!"}), 200

# Start de server
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        update_reservaties_route() 
    app.run(debug=True)