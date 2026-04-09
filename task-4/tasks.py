import time
import random

def send_welcome_email(email):
    print(f"[WORK] Sending email to {email}")
    time.sleep(1)
    if random.choice([True, False]):
        raise Exception("SMTP connection failed")
    return f"email_sent"

def resize_product_image(image_id, width, height):
    print(f"[WORK] Resizing image {image_id} to {width}x{height}")
    time.sleep(2)
    if random.choice([True, False]):
        raise Exception("Image processing error")
    return f"{image_id}_{width}x{height}.jpg"

def process_payment(amount, card):
    print(f"[WORK] Processing payment ${amount} with {card}")
    time.sleep(1.5)
    if random.choice([True, False]):
        raise Exception("Payment failed")
    return f"payment_{amount}_approved"

def backup_database():
    print("[WORK] Backing up database")
    time.sleep(3)
    if random.choice([True, False]):
        raise Exception("Backup failed")
    return "backup_success"

def send_slack_notification(message):
    print(f"[WORK] Sending Slack: {message}")
    time.sleep(0.5)
    if random.choice([True, False]):
        raise Exception("Slack send failed")
    return "notification_sent"

def sync_to_crm(user_id):
    print(f"[WORK] Syncing user {user_id} to CRM")
    time.sleep(2)
    if random.choice([True, False]):
        raise Exception("CRM sync failed")
    return f"user_{user_id}_synced"
