import json
import smtplib
import ssl
from email.message import EmailMessage

from celery import Celery

from core.settings import settings


app = Celery(
    broker=settings.broker_url, broker_connection_retry_on_startup=True
)


@app.task
def send_email(json_data: str):
    data = json.loads(json_data)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        settings.SMTP_SERVER, settings.EMAIL_PORT, context=context
    ) as server:
        msg = EmailMessage()
        msg.set_content(data["message"])
        msg["Subject"] = data["subject"]
        sender_email = settings.SENDER_EMAIL
        password = settings.EMAIL_PASSWORD
        server.login(sender_email, password)  # type: ignore[arg-type]
        server.send_message(msg, sender_email, data["receiver_emails"])
