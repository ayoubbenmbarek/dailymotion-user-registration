from abc import ABC, abstractmethod
from email.mime.text import MIMEText

import aiosmtplib

from app.config import settings


class EmailServiceInterface(ABC):
    """Abstract interface for email services."""

    @abstractmethod
    async def send_activation_code(self, email: str, code: str) -> bool:
        """Send an activation code to the user's email."""
        pass


class SMTPEmailService(EmailServiceInterface):
    """SMTP email service implementation using MailHog."""

    def __init__(self, host: str = None, port: int = None):
        self.host = host or settings.smtp_host
        self.port = port or settings.smtp_port

    async def send_activation_code(self, email: str, code: str) -> bool:
        """Send an activation code via SMTP to MailHog."""
        message = MIMEText(
            f"Your activation code is: {code}\n\n"
            f"This code will expire in 1 minute.\n\n"
            f"If you did not request this code, please ignore this email."
        )
        message["Subject"] = "Your Dailymotion Activation Code"
        message["From"] = "noreply@dailymotion.com"
        message["To"] = email

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
            )
            return True
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
            return False


class ConsoleEmailService(EmailServiceInterface):
    """Console email service for testing/development."""

    async def send_activation_code(self, email: str, code: str) -> bool:
        """Print the activation code to console."""
        print(f"\n{'='*50}")
        print(f"ACTIVATION CODE for {email}")
        print(f"Code: {code}")
        print(f"{'='*50}\n")
        return True
