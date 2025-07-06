import random
import smtplib
from email.mime.text import MIMEText

def test_smtp():
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "pilot.fish24@gmail.com"
    password = "aslsblojjdtrkfhp"  # Remplace par ton vrai mot de passe d'application
    code = str(random.randint(100000, 999999))
    receiver_email = "fouadkacemi20@gmail.com"
    message = MIMEText(f"Test d'email depuis script SMTP simple. Code : {code}\n\nvoila le code")
    message["Subject"] = "Test SMTP"
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email envoyé avec succès.")
    except Exception as e:
        print("Erreur SMTP:", e)

test_smtp()
