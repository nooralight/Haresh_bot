from flask import Flask, render_template, request, jsonify,session, redirect, url_for
from flask_session import Session
from twilio.rest import Client

from datetime import datetime,timedelta

import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['secret_key'] = '5800d5d9e4405020d527f0587538abbe'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
phone_number = os.getenv('PHONE_NUMBER')
twilio_client = Client(account_sid, auth_token)

@app.route('/whatsapp', methods=['POST'])
def handle_incoming_message():
    message = request.form.get('Body')
    sender = request.form.get('From')
    profile_name = request.form.get('ProfileName')
    media_url = request.form.get('MediaUrl0')
    print("hello")
    if media_url:
        message_send = twilio_client.messages.create(
            from_ = phone_number,
            body=f"Hi {profile_name}, I am Haresh from Pedal Court. It seems like you sent a media file to me. New version will come very soon.",
            to= sender
        )
    else:
        message_send = twilio_client.messages.create(
            from_ = phone_number,
            body=f"Hi {profile_name}, I am Haresh from Pedal Court. Thanks for sending message to me. New version will come very soon.",
            to= sender
        )
    
    return "okay",200

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)