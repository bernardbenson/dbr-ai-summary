import os
import pandas as pd
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIG ===
BIBLE_ID = "de4e12af7f28f599-02"  # ESV
API_KEY = os.getenv("BIBLE_API_KEY")  # safer than hardcoding
if not API_KEY:
    API_KEY = "42794886f5801c9352dcdac6128aaac8"  # fallback
headers = {"api-key": API_KEY}

# === Load reading plan ===
bible_readings = pd.read_excel('/Users/cahabaheightschurch/bible_reading/bible_reading_2025.xlsx')

def format_reading_list(reading):
    """Take 'John 3:16, Psalm 23' and make a list of passages."""
    return [part.strip() for part in reading.split(',') if part.strip()]

def get_passage(reference: str) -> str:
    """Fetch formatted passage text from api.bible as HTML."""
    search_url = f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/search"
    params = {"query": reference}
    search_response = requests.get(search_url, headers=headers, params=params)
    search_data = search_response.json()

    if not search_data.get("data", {}).get("verses"):
        return f"<p><em>No results found for {reference}</em></p>"

    verses = search_data["data"]["verses"]
    first_id = verses[0]["id"]
    last_id = verses[-1]["id"]

    passage_id = f"{first_id}-{last_id}"
    passage_url = f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/passages/{passage_id}"
    passage_response = requests.get(passage_url, headers=headers)
    passage_data = passage_response.json()

    return passage_data["data"]["content"]

def send_email(subject, html_body, recipients, sender_name):
    from_email = "cahabaheightschurch@gmail.com"
    from_password = "oefc sldb vlem yyrj"  # app password

    formatted_from = f"{sender_name} <{from_email}>"

    msg = MIMEMultipart("alternative")
    msg['From'] = formatted_from
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject

    # Attach both plain text (fallback) and HTML
    msg.attach(MIMEText("This email requires HTML view.", 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, recipients, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# === Main flow ===
today = datetime.now()
day_of_week = today.strftime('%A')

if day_of_week in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
    reading = bible_readings[bible_readings['date'] == today.strftime('%Y-%m-%d')]
    if not reading.empty:
        subject = f"Daily Bible Reading for {today.strftime('%x')}"
        passages = format_reading_list(reading['reading'].values[0])

        # Build email body
        html_body = f"<h2>Today's Readings ({today.strftime('%x')})</h2><ul>"
        for ref in passages:
            html_body += f"<li><strong>{ref}</strong></li>"
        html_body += "</ul><hr>"

        # Add formatted scripture text
        for ref in passages:
            html_body += f"<h3>{ref}</h3>"
            html_body += get_passage(ref)

        recipients = ['cahabachurch@googlegroups.com','bernardbenson.dl@gmail.com']
        send_email(subject, html_body, recipients, "Cahaba Heights church of Christ")
    else:
        print("No reading for today.")
else:
    print("No email sent. It's the weekend!")
