import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import sys

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_RECIPIENTS, EMAIL_FROM


def send_report(pdf_path: Path, month_label: str) -> None:
    """
    Sends the generated PDF report to all recipients in EMAIL_RECIPIENTS.
    """
    subject = f"{month_label} Sales Report"
    body = f"Please find attached the sales report for {month_label}."

    # Build MIME message
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)
    msg["Subject"] = subject

    # Body
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={pdf_path.name}",
        )
        msg.attach(part)

    # Send
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_RECIPIENTS, msg.as_string())

    print(f"Email sent to: {', '.join(EMAIL_RECIPIENTS)}")
