import smtplib
from email.mime.multipart import MIMEMultipart

from pydantic import EmailStr

from src.config import config


def send_email(email_to: EmailStr, text):
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        message = MIMEMultipart("alternative")
        message["Subject"] = f"{text}"
        message["From"] = config.SMTP_USERNAME

        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USERNAME, email_to, message.as_string())