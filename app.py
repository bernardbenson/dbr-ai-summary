import os
import re
import pandas as pd
import smtplib
import requests
import ollama
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === CONFIG ===
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

BIBLE_ID = "de4e12af7f28f599-02"  # ESV
API_KEY = os.getenv("BIBLE_API_KEY")
if not API_KEY:
    raise ValueError("BIBLE_API_KEY environment variable is required. Please set it with your API key from api.scripture.api.bible")
headers = {"api-key": API_KEY}

# === Load reading plan ===
bible_readings = pd.read_excel('bible_reading_2025.xlsx')

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

def generate_summary_and_takeaways(passages_text: str) -> dict:
    """Generate AI summary and key takeaways aligned with Church of Christ doctrine."""
    prompt = f"""You are a Bible teacher from the Church of Christ tradition.
Please analyze the following scripture passages and provide:

1. A concise summary (2-3 paragraphs) of the main themes and messages in these passages
2. 3-5 key takeaways that draw practical or doctrinal insights from the text

When appropriate, consider Church of Christ values such as the authority of Scripture, the importance of faith and obedience, biblical worship, and faithful Christian living. However, focus primarily on what the text itself teaches - don't present any summaries or takeaways that disagrees with the church of christ doctrine.

Scripture passages:
{passages_text}

Format your response as:
SUMMARY:
[Your summary here]

KEY TAKEAWAYS:
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]
etc.
"""

    try:
        response = ollama.chat(
            model='gpt-oss:20b',
            messages=[{'role': 'user', 'content': prompt}]
        )

        content = response['message']['content']

        # Parse the response
        parts = content.split('KEY TAKEAWAYS:')
        summary = parts[0].replace('SUMMARY:', '').strip()
        takeaways = parts[1].strip() if len(parts) > 1 else ''

        return {
            'summary': summary,
            'takeaways': takeaways
        }
    except Exception as e:
        print(f"Error generating summary: {e}")
        return {
            'summary': 'Unable to generate summary at this time.',
            'takeaways': ''
        }

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

# Test mode: Find today's date or the nearest weekday with a reading
if TEST_MODE:
    print("🧪 TEST MODE ENABLED")
    # Filter for dates >= today
    future_readings = bible_readings[
        (bible_readings['date'].notna()) &
        (pd.to_datetime(bible_readings['date']) >= today.replace(hour=0, minute=0, second=0, microsecond=0))
    ]
    if not future_readings.empty:
        # Pick the first weekday reading
        for idx, row in future_readings.iterrows():
            test_date = pd.to_datetime(row['date'])
            test_day = test_date.strftime('%A')
            if test_day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                today = test_date
                day_of_week = test_day
                print(f"Using test date: {today.strftime('%Y-%m-%d')} ({day_of_week})")
                break

if day_of_week in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
    reading = bible_readings[bible_readings['date'] == today.strftime('%Y-%m-%d')]
    if not reading.empty:
        subject = f"Daily Bible Reading for {today.strftime('%x')}"
        passages = format_reading_list(reading['reading'].values[0])

        # Fetch all passages and collect text
        print("Fetching scripture passages...")
        passages_html = ""
        passages_plain_text = ""

        for ref in passages:
            passage_html = get_passage(ref)
            passages_html += f"<h3>{ref}</h3>{passage_html}"
            # Strip HTML tags for plain text version (simple approach)
            plain = re.sub('<[^<]+?>', '', passage_html)
            passages_plain_text += f"\n{ref}\n{plain}\n"

        # Generate AI summary and takeaways
        print("Generating AI summary and takeaways...")
        ai_content = generate_summary_and_takeaways(passages_plain_text)

        # Build email body with scripture readings first, then summary
        html_body = f"<h2>Daily Bible Reading for {today.strftime('%x')}</h2>"

        # List passages first
        html_body += "<h3>Today's Scripture Readings</h3>"
        html_body += "<ul>"
        for ref in passages:
            html_body += f"<li><strong>{ref}</strong></li>"
        html_body += "</ul><hr>"

        # Add AI Summary
        html_body += "<h3>Summary</h3>"
        # Convert **text** to <strong>text</strong> in summary
        summary_formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', ai_content['summary'])
        html_body += f"<p>{summary_formatted.replace(chr(10), '</p><p>')}</p>"

        # Add Key Takeaways
        if ai_content['takeaways']:
            html_body += "<h3>Key Takeaways</h3>"
            # Convert markdown list to HTML and handle **bold** markdown
            takeaway_lines = ai_content['takeaways'].split('\n')
            html_body += "<ul>"
            for line in takeaway_lines:
                if line.strip().startswith('-'):
                    # Convert **text** to <strong>text</strong>
                    formatted_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line.strip()[1:].strip())
                    html_body += f"<li>{formatted_line}</li>"
            html_body += "</ul>"

        # Use test recipient in test mode
        if TEST_MODE:
            recipients = ['bernardbenson.dl@gmail.com', 'jlselby231@gmail.com']
            print(f"📧 Sending test email to: {recipients}")
        else:
            recipients = ['cahabachurch@googlegroups.com','bernardbenson.dl@gmail.com']

        send_email(subject, html_body, recipients, "Cahaba Heights church of Christ")
    else:
        print("No reading for today.")
else:
    print("No email sent. It's the weekend!")
