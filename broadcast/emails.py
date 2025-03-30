import json
import httpx
from typing import Any
import logging
from pathlib import Path
from dataclasses import dataclass
from syft_core import Client


# Set up SyftBox client
client = Client.load()
api_name = client.api_request_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"{api_name}:{Path(__file__).name}")

api_data_dir = client.api_data()
api_data_dir.mkdir(parents=True, exist_ok=True)
email_queue_json = api_data_dir / "email_queue.json"

MAX_EMAIL_RETRIES = 3
EMAIL_API_URL = "https://syftbox.openmined.org/emails/"
EMAIL_SUBJECT = "SyftBox: New API request received ({api_request_name})"
EMAIL_TEMPLATE = Path(__file__).parent / "email_template.html"
SYFTBOX_LOGO_URL = "https://syftbox.openmined.org/icon.png"


@dataclass
class EmailQueueEntry:
    recipient: str
    api_request_name: str
    sender: str
    retries: int = 0


class EmailService:
    @classmethod
    def read_email_queue(cls) -> list[dict[str, Any]]:
        if email_queue_json.exists():
            with open(email_queue_json, "r") as f:
                return json.load(f)
        return []

    @classmethod
    def write_email_queue(cls, queue: list[dict[str, Any]]) -> None:
        with open(email_queue_json, "w") as f:
            json.dump(queue, f)

    @classmethod
    def send_email(cls, sender: str, recipient: str, api_request_name: str) -> None:
        html = (
            EMAIL_TEMPLATE.read_text()
            .replace("{{logo_url}}", SYFTBOX_LOGO_URL)
            .replace("{{sender_email}}", sender)
            .replace("{{recipient_name}}", recipient.split("@")[0].capitalize())
            .replace("{{recipient_email}}", recipient)
            .replace("{{api_request_name}}", api_request_name)
        )
        json_data = {
            "to": recipient,
            "subject": EMAIL_SUBJECT.format(api_request_name=api_request_name),
            "html": html,
        }
        logger.info(f"Sending email to '{recipient}' for '{api_request_name}'")
        try:
            with httpx.Client() as client:
                response = client.post(EMAIL_API_URL, json=json_data)
                response.raise_for_status()
                logger.info(f"✅ Email sent successfully to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    @classmethod
    def add_to_email_queue(
        cls, recipient: str, api_request_name: str, sender: str
    ) -> None:
        email_queue = cls.read_email_queue()
        entry = EmailQueueEntry(recipient, api_request_name, sender).__dict__
        email_queue.append(entry)
        cls.write_email_queue(email_queue)
        logger.info(f"Added email to queue for {recipient}")

    @classmethod
    def process_email_queue(cls) -> None:
        email_queue = cls.read_email_queue()
        if not email_queue:
            logger.info("No emails to send. Email queue is empty.")
            return

        while email_queue:
            entry = email_queue[0]
            try:
                cls.send_email(
                    entry["sender"], entry["recipient"], entry["api_request_name"]
                )
                email_queue.pop(0)
                cls.write_email_queue(email_queue)
                logger.info(f"Email sent successfully to {entry['recipient']}")
            except Exception as e:
                entry["retries"] += 1
                logger.warning(
                    f"Failed to send email to {entry['recipient']}: {e}. "
                    f"Attempts remaining: {MAX_EMAIL_RETRIES - entry['retries']}"
                )
                if entry["retries"] >= MAX_EMAIL_RETRIES:
                    logger.error(f"Max retries reached for {entry['recipient']}")
                    email_queue.pop(0)
                cls.write_email_queue(email_queue)
