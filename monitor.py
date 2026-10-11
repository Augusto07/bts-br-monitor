import os
import logging
import requests
import smtplib
from pathlib import Path
from email.message import EmailMessage

API_URL = "https://btspopuplatam.com/api/campaigns"
SHOWS_URL = "https://btspopuplatam.com/shows"
NOTIFIED_FILE = Path(__file__).with_name("notified.txt")

logging.basicConfig(level=logging.INFO)


def send_email(recipient, subject, body):
    sender = os.getenv("GMAIL_URL")
    password = os.getenv("GMAIL_APP_PWD")

    if not sender or not password:
        raise ValueError("Configure GMAIL_URL and GMAIL_APP_PWD.")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(sender, password)
        server.send_message(message)


def check_show():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    shows = response.json()

    if not isinstance(shows, list):
        raise ValueError("Unexpected API response format.")

    return any(
        show.get("country") == "BR"
        for show in shows
    )


def main():
    recipient = os.getenv("DEST_EMAIL")

    if not recipient:
        raise ValueError("Configure DEST_EMAIL.")

    if NOTIFIED_FILE.exists():
        logging.info("Notification already sent.")
        return

    try:
        if check_show():
            send_email(
                recipient=recipient,
                subject="BTS LIBERO BRASIL CORREEEEEEEE",
                body=f"Brazilian popup found!\n\n{SHOWS_URL}"
            )

            NOTIFIED_FILE.write_text("sent", encoding="utf-8")
            logging.info("Notification sent successfully.")
        else:
            logging.info("No Brazilian popup found.")

    except (
        requests.RequestException,
        smtplib.SMTPException,
        ValueError,
        OSError
    ):
        logging.exception("Monitoring failed.")
        raise


if __name__ == "__main__":
    main()
