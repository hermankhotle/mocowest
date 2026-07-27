from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging
import threading
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Gmail SMTP Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'hermankhotle@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'hermankhotle@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Initialize extensions
csrf = CSRFProtect(app)
mail = Mail(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make CSRF token available to all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Function to send email in background
def send_email_async(data):
    try:
        with app.app_context():
            msg_body = f"""New contact form submission:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}
Message:
{data['message']}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            msg = Message(
                subject=f"MOCOWEST Contact Form: {data['subject']}",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[app.config['MAIL_DEFAULT_SENDER']],
                body=msg_body,
                reply_to=data['email']
            )
            
            mail.send(msg)
            logger.info(f"✅ Email sent successfully to {data['email']}")
    except Exception as e:
        logger.error(f"❌ Email error: {str(e)}")

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
            
            # Send email in background (don't wait for it)
            if app.config['MAIL_PASSWORD']:
                thread = threading.Thread(target=send_email_async, args=(data,))
                thread.daemon = True
                thread.start()
                logger.info("📧 Email queued for sending")
            else:
                logger.warning("⚠️ Email password not configured - email not sent")
            
            # Return success immediately (don't wait for email)
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
