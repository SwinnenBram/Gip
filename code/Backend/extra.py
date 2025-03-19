def send_confirmation_email(reservering, nummerplaat, locatie, email):
    print('In de send_confirmation_email functie')

    # E-mailgegevens
    sender_email = "bramswinnen1@gmail.com"
    receiver_email = email  # Het e-mailadres van de klant
    subject = f"Bevestiging van reservering {reservering.reservatienummer}"
    
    body = f"""
    Beste klant,

    Je reservering met nummer {reservering.reservatienummer} is bevestigd.

    Voertuig nummerplaat: {nummerplaat}
    Reserveringsdatum: {date.today()}
    Starttijd: {reservering.starttijd}
    Eindtijd: {reservering.eindtijd}
    Parkeerplaatslocatie: {locatie}

    Bedankt voor je reservering!
    """

    html = f"""
    <h2>Bevestiging van reservering {reservering.reservatienummer}</h2>
    <p>Beste klant,</p>
    <p>Je reservering met nummer <strong>{reservering.reservatienummer}</strong> is bevestigd.</p>
    <p><strong>Voertuig nummerplaat:</strong> {nummerplaat}</p>
    <p><strong>Reserveringsdatum:</strong> {date.today()}</p>
    <p><strong>Starttijd:</strong> {reservering.starttijd}</p>
    <p><strong>Eindtijd:</strong> {reservering.eindtijd}</p>
    <p><strong>Parkeerplaatslocatie:</strong> {locatie}</p>
    <p>Bedankt voor je reservering!</p>
    """

    # Maak de e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEText(html, 'html'))

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