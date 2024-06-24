from flask import Flask, request, jsonify,session, render_template
from flask_session import Session
from twilio.rest import Client
from mongoengine import *
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
messaging_sid=os.getenv('MESSAGING_SID')
twilio_client = Client(account_sid, auth_token)

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

# Define the MongoDB document schema using mongoengine
class Contacts(Document):
    id = SequenceField(primary_key=True)
    name = StringField()
    whatsapp = StringField()
    last_message = StringField()
    created_at = DateTimeField()

class Message_db(Document):
    id = SequenceField(primary_key=True)
    user_number = StringField()
    message = StringField()
    user_type =StringField()
    created_at = DateTimeField()


def insert_into_message(user_number, message , user_type):
    new_msg = Message_db(
        user_number = user_number,
        message = message,
        user_type = user_type,
        created_at = datetime.now()
    )
    new_msg.save()


def insert_into_contacts(name , whatsapp):
    contact = Contacts(
        name = name,
        whatsapp = whatsapp,
        created_at = datetime.now()
    )
    contact.save()
    return contact

@app.route('/', methods=['POST','GET'])
def home():
    return render_template("home.html")

@app.route('/bookings', methods=['POST','GET'])
def bookings():
    return render_template("bookings.html")

@app.route('/players', methods=['POST','GET'])
def players():
    return render_template("players.html")

@app.route('/contacts', methods=['POST','GET'])
def contacts():
    contacts = Contacts.objects()
    return render_template("chat_page.html",contacts = contacts)

@app.route('/message_history/<contact_id>', methods=['GET'])
def message_history(contact_id):
    messages = Message_db.objects(user_number=contact_id)
    return jsonify(messages)

@app.route('/message_history/<whatsapp>', methods=['GET'])
def message_history(whatsapp):
    messages = Message_db.objects(user_number=whatsapp)
    return jsonify(messages)

@app.route('/whatsapp', methods=['POST'])
def handle_incoming_message():
    message = request.form.get('Body')
    sender = request.form.get('From')
    profile_name = request.form.get('ProfileName')
    media_url = request.form.get('MediaUrl0')
    print("hello")
    # Checking if user already available
    already_user = Contacts.objects(whatsapp = sender[9:]).first()
    if not already_user:
        new_created = insert_into_contacts(profile_name, sender[9:])
        new_created.last_message = message
        new_created.save()
    else:
        already_user.last_message = message
        already_user.save()

    insert_into_message(sender[9:],message, "user")
    if media_url:
        message_send = twilio_client.messages.create(
            from_ = phone_number,
            body=f"Hi {profile_name}, I am Haresh from Pedal Court. It seems like you sent a media file to me. New version will come very soon.",
            to= sender
        )
    else:
        if session.get('context') == None or 'context' not in session:
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HXf277f17ed523bd7e6cbecc9388fc1912",
                    to = sender
                )
        
            session['context'] = "started"
            return "okay",200
        elif session.get('context') == "started":
            message_send = twilio_client.messages.create(
                    from_ = phone_number,
                    body=f"Hi {profile_name}, I am Haresh from Pedal Court. Right now it's in testing stage. We will update the chatbot shortly. Thank you!",
                    to= sender
                )
            session['context'] = None
            return "okay",200

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)