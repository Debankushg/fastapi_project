import smtplib
from email.headerregistry import Address
from email.message import EmailMessage

from app.core.config import settings
from app.core.i18n import DEFAULT_LANGUAGE, translate

MAIL_FROM_NAME = "Ottogusto Support Team"


def send_email(*, to: str, subject: str, html_body: str) -> None:
    message = EmailMessage()
    message["From"] = Address(display_name=MAIL_FROM_NAME, addr_spec=settings.MAIL_FROM)
    message["To"] = to
    message["Subject"] = subject
    message.set_content("This email requires an HTML-capable mail client.")
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(message)


def send_otp_email(
    *, to: str, otp_code: str, expire_minutes: int, language: str = DEFAULT_LANGUAGE
) -> None:
    subject = translate(language, "otp_email.subject")
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
        <p>{translate(language, "otp_email.greeting")}</p>

        <p>{translate(language, "otp_email.intro")}</p>

        <p style="font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #111111;">
            {otp_code}
        </p>

        <p>
            {translate(language, "otp_email.expiry", minutes=expire_minutes)}
        </p>

        <p>
            {translate(language, "otp_email.warning")}
        </p>

        <p>
            {translate(language, "otp_email.regards")}<br>
            <strong>{MAIL_FROM_NAME}</strong>
        </p>
    </body>
    </html>
    """

    send_email(to=to, subject=subject, html_body=html_body)
