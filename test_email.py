# test_email.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)

# Gmail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hermankhotle@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'hjwfzyxyhafgopqh'      # Your app password (no spaces)
app.config['MAIL_DEFAULT_SENDER'] = 'hermankhotle@gmail.com'

mail = Mail(app)

print("=" * 50)
print("Testing Gmail SMTP Configuration")
print("=" * 50)
print(f"Server: {app.config['MAIL_SERVER']}")
print(f"Port: {app.config['MAIL_PORT']}")
print(f"Username: {app.config['MAIL_USERNAME']}")
print(f"Password: {'*' * 16}")
print(f"Sender: {app.config['MAIL_DEFAULT_SENDER']}")
print("=" * 50)
print()

with app.app_context():
    try:
        msg = Message(
            subject="Test Email from MOCOWEST",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['hermankhotle@gmail.com'],  # Send to yourself to test
            body="✅ This is a test email from MOCOWEST!\n\nIf you received this, your contact form is working!"
        )
        mail.send(msg)
        print("✅ Email sent successfully!")
        print("   Check your Gmail inbox.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure you used the app password (not your regular password)")
        print("2. Remove any spaces from the app password")
        print("3. Make sure 2-Step Verification is enabled in your Google account")