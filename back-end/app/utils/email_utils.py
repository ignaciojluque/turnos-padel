from flask_mail import Message
from app.extensiones import mail

def enviar_email(destinatario, asunto, cuerpo):
    msg = Message(subject=asunto, recipients=[destinatario])
    msg.body = cuerpo
    mail.send(msg)
