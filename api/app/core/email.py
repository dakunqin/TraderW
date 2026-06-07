import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_email(to_email: str, subject: str, text_body: str) -> None:
    if not settings.smtp_host or not settings.smtp_from:
        raise RuntimeError("SMTP not configured")

    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_body)

    smtp_cls = smtplib.SMTP_SSL if settings.smtp_ssl else smtplib.SMTP
    with smtp_cls(settings.smtp_host, settings.smtp_port, timeout=20) as s:
        s.ehlo()
        if settings.smtp_starttls and not settings.smtp_ssl:
            s.starttls()
            s.ehlo()
        if settings.smtp_username:
            s.login(settings.smtp_username, settings.smtp_password)
        s.send_message(msg)
