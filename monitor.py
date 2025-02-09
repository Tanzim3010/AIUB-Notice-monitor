import smtplib
import hashlib
import time
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration from .env file
URL = "https://www.aiub.edu/category/notices"
CHECK_INTERVAL = 60  # Check every 60 seconds
GMAIL_USER = os.getenv("GMAIL_USER")  # Fetch from .env
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Fetch from .env
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # Fetch from .env

# Function to get page content hash and extract meaningful text
def get_page_content():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    notices = soup.find_all('div', class_='info')  # Adjusted to match the "info" class
    latest_notice = notices[0].text.strip() if notices else "No new notices"
    return latest_notice, hashlib.md5(latest_notice.encode()).hexdigest()

# Function to send a fancy email via Gmail's SMTP server
def send_email(subject, body):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        # Add body to email (HTML content for a more fancy email)
        html_body = f"""
        <html>
        <body>
            <h2 style="color: #4CAF50;">New AIUB Notice</h2>
            <p>{body}</p>
            <a href="https://www.aiub.edu/category/notices" style="color: #008CBA;">Click here to view all notices</a>
            <br>
            <p style="color: #888;">This is an automated notification. Please do not reply.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        # Create a secure SSL context and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

# Test function to verify Gmail connection
def test_gmail_connection():
    print("Testing Gmail SMTP connection...")
    try:
        subject = "Test Email"
        body = "This is a test email from Gmail SMTP."
        send_email(subject, body)
    except Exception as e:
        print(f"Error sending test email: {e}")

# Monitoring loop
if __name__ == "__main__":
    previous_notice, previous_hash = get_page_content()
    print("Monitoring started...")

    # Test Gmail connection before proceeding
    test_gmail_connection()

    # Send the initial test email to ensure the system works
    print("Sending test email...")
    send_email("Test Notice", "This is a test email to verify the monitor works.")

    # Fake change for testing: Modify the previous hash manually to simulate a change
    #previous_hash = "fakehash"  # Force a change

    while True:
        time.sleep(CHECK_INTERVAL)
        latest_notice, current_hash = get_page_content()

        if current_hash != previous_hash:
            print("Change detected! Sending email...")
            subject = f"New Notice: {latest_notice[:50]}..."  # Extract a meaningful subject
            body = f"Hey! AIUB dropped a new notice on {latest_notice[:50]}..."  # Custom body
            send_email(subject, body)
            previous_notice, previous_hash = latest_notice, current_hash

            # After testing, reset the previous_hash to simulate a new check cycle
            previous_hash = current_hash  # Avoid continuous email sending after a single change
