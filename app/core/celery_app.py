import json
import smtplib
import ssl
from email.message import EmailMessage

from celery import Celery

from core.settings import config


app = Celery(broker=config.broker_url, broker_connection_retry_on_startup=True)


@app.task
def send_email(json_data: str):
    data = json.loads(json_data)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        config.SMTP_SERVER, config.EMAIL_PORT, context=context
    ) as server:
        msg = EmailMessage()
        msg.set_content(data["message"])
        msg["Subject"] = data["subject"]
        server.login(config.SENDER_EMAIL, config.EMAIL_PASSWORD)
        server.send_message(msg, config.SENDER_EMAIL, data["receiver_emails"])
