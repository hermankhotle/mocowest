from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv
import os
import logging
import threading
from datetime import datetime
from mailersend import MailerSendClient, EmailBuilder

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize CSRF
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make CSRF token available to all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Initialize MailerSend
mailersend_api_key = os.getenv('MAILERSEND_API_KEY')
mailersend_from_email = os.getenv('MAILERSEND_FROM_EMAIL', 'admin@mocowest.co.za')
mailersend_to_email = os.getenv('MAILERSEND_TO_EMAIL', 'hermankhotle@gmail.com')

# Function to send email using MailerSend
def send_email_async(data):
    try:
        if not mailersend_api_key:
            logger.error("❌ MailerSend API key not configured")
            return
        
        # Initialize MailerSend client
        ms = MailerSendClient(mailersend_api_key)
        
        # Build email
        email_body = f"""
New contact form submission from MOCOWEST:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}
Message:
{data['message']}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Reply to: {data['email']}
"""
        
        email = (EmailBuilder()
                 .from_email(mailersend_from_email, "MOCOWEST Website")
                 .to_many([{"email": mailersend_to_email, "name": "MOCOWEST Team"}])
                 .subject(f"MOCOWEST Contact Form: {data['subject']}")
                 .text(email_body)
                 .html(f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #1a2a6c; color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
        .field {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #1a2a6c; }}
        .value {{ color: #333; }}
        .footer {{ margin-top: 20px; text-align: center; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>📬 New Contact Form Submission</h2>
        <p style="color: rgba(255,255,255,0.8);">MOCOWEST Cloud Platform</p>
    </div>
    <div class="content">
        <div class="field"><span class="label">Name:</span> <span class="value">{data['name']}</span></div>
        <div class="field"><span class="label">Email:</span> <span class="value">{data['email']}</span></div>
        <div class="field"><span class="label">Subject:</span> <span class="value">{data['subject']}</span></div>
        <div class="field"><span class="label">Message:</span></div>
        <div class="value" style="background: white; padding: 10px; border-radius: 5px; margin-top: 5px;">{data['message']}</div>
        <div class="field" style="margin-top: 15px;"><span class="label">Submitted:</span> <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span></div>
        <hr style="margin: 20px 0; border: 1px solid #ddd;">
        <p style="color: #666; font-size: 14px;">Reply to: <a href="mailto:{data['email']}">{data['email']}</a></p>
    </div>
    <div class="footer">
        <p>This email was sent from MOCOWEST Contact Form</p>
        <p>&copy; 2026 MOCOWEST Cloud Platform</p>
    </div>
</body>
</html>
""")
                 .build())
        
        # Send email
        response = ms.emails.send(email)
        
        # Check response - MailerSend returns 202 on success
        logger.info(f"✅ Email sent successfully to {mailersend_to_email}")
        logger.info(f"   Status Code: {response.status_code if hasattr(response, 'status_code') else 'Unknown'}")
        logger.info(f"   From: {data['email']}")
        logger.info(f"   Subject: {data['subject']}")
        
        # Try to get message_id if available
        if hasattr(response, 'message_id'):
            logger.info(f"   Message ID: {response.message_id}")
        elif hasattr(response, 'data') and hasattr(response.data, 'message_id'):
            logger.info(f"   Message ID: {response.data.message_id}")
        
    except Exception as e:
        logger.error(f"❌ MailerSend error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/industries')
def industries():
    return render_template('industries.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
            
            logger.info(f"Contact form data received from: {data.get('email', 'unknown')}")
            
            # Validate required fields
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Send email in background
            if mailersend_api_key:
                thread = threading.Thread(target=send_email_async, args=(data,))
                thread.daemon = True
                thread.start()
                logger.info("📧 Email queued for sending via MailerSend")
            else:
                logger.warning("⚠️ MailerSend API key not configured - email not sent")
            
            # Return success immediately
            return jsonify({
                'success': True,
                'message': 'Message sent successfully! We will get back to you soon.'
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Contact form error: {str(e)}")
            return jsonify({'error': 'Failed to send message. Please try again.'}), 500
    
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

@app.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@app.route('/robots.txt')
def robots():
    return render_template('robots.txt'), 200, {'Content-Type': 'text/plain'}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1', host='0.0.0.0', port=port)