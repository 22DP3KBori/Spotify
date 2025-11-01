import os
from dotenv import load_dotenv
import requests

# ✅ Load .env inside this file too
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

API_KEY = os.getenv("MAILGUN_API_KEY")
DOMAIN = os.getenv("MAILGUN_DOMAIN")
FROM_EMAIL = os.getenv("MAILGUN_FROM")

def send_email(to, subject, text):
    if not API_KEY or not DOMAIN or not FROM_EMAIL:
        print("❌ Mailgun env vars missing!")
        print("api:", API_KEY)
        print("domain:", DOMAIN)
        print("sender:", FROM_EMAIL)
        return False

    return requests.post(
        f"https://api.mailgun.net/v3/{DOMAIN}/messages",
        auth=("api", API_KEY),
        data={
            "from": FROM_EMAIL,
            "to": to,
            "subject": subject,
            "text": text
        }
    )
