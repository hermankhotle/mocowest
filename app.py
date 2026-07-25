from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'mail.mocowest.co.za')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

csrf = CSRFProtect(app)
mail = Mail(app)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                msg_body = f"""New contact form submission:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}
Message:
{data['message']}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                
                msg = Message(
                    subject=f"Contact Form: {data['subject']}",
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[app.config['MAIL_USERNAME']],
                    body=msg_body
                )
                mail.send(msg)
                logger.info(f"Contact form submitted by {data['email']}")
            
            return jsonify({'success': True, 'message': 'Message sent successfully!'}), 200
        except Exception as e:
            logger.error(f"Contact form error: {str(e)}")
            return jsonify({'error': 'Failed to send message. Please try again.'}), 500
    return render_template('contact.html')

# Policy Pages
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
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

    