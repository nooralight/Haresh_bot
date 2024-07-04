from flask import Flask, request, jsonify,session, render_template, redirect, url_for
from flask_session import Session
from twilio.rest import Client
from mongoengine import *
from datetime import datetime,timedelta
from db_player import add_new_player, update_player
from db_booking import insert_new_booking

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

class Admin_user(Document):
    id = SequenceField(primary_key=True)
    name = StringField()
    email = StringField()
    designation = StringField()
    role = StringField()
    password = StringField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

class Players(Document):
    id = SequenceField(primary_key=True)
    name = StringField()
    mobile = StringField()
    age = StringField()
    sex = StringField()
    level = StringField()
    availability = StringField()
    preferred_position = StringField()
    dominant_hand = StringField()
    status = StringField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

class Match_booking(Document):
    id = SequenceField(primary_key=True)
    booking_datetime = DateTimeField()
    court_name = StringField()
    match_number = StringField()
    player_count = IntField()
    players_whatsapp = ListField(StringField())
    state = StringField()
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
    numOfcontacts = Contacts.objects().count()
    numOfmessages = Message_db.objects().count()
    numOfplayers = Players.objects().count()
    return render_template("home.html", numOfcontacts = numOfcontacts, numOfmessages = numOfmessages, numOfplayers = numOfplayers)

@app.route('/bookings', methods=['POST','GET'])
def bookings():
    return render_template("bookings.html")

@app.route('/add_new_booking', methods=['POST','GET'])
def add_new_booking():
    if request.method == "POST":
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        event_court = request.form.get('event_court')
        event_capacity = request.form.get('event_capacity')
        event_status = request.form.get('event_status')
        event_match_no = request.form.get('event_match_no')
        players_whatsapp_list = request.form.getlist('player_whatsapp[]')
        final_player_list = []
        for item in players_whatsapp_list:
            if item!= "":
                final_player_list.append(item)
        insert_new_booking(event_date, event_time, event_court, event_match_no, event_capacity, final_player_list, event_status)

        return redirect(url_for('bookings'))
    return render_template("add_event.html")

@app.route('/players', methods=['POST','GET'])
def players():
    players = Players.objects().order_by('-id')
    return render_template("players.html", players = players)



@app.route('/add_new_player', methods=['POST','GET'])
def create_new_player():
    if request.method == "POST":
        name = request.form.get('p_name')
        mobile = request.form.get('p_mobile')
        age = request.form.get('p_age')
        sex = request.form.get('p_sex')
        level = request.form.get('p_level')
        status = "Active"
        add_new_player(name, mobile, age, sex, level, status)

        return redirect(url_for('players'))
    
    return render_template('add_player.html')

@app.route('/edit_player', methods=['POST','GET'])
def edit_player():
    referrer = request.referrer # Previous Link
    # TODO
    player_id = request.form.get('player_id')
    new_name = request.form.get('new_name')
    new_mobile = request.form.get('new_mobile')
    new_age = request.form.get('new_age')
    new_sex = request.form.get('new_sex')
    new_level = request.form.get('new_level')
    new_status = request.form.get('new_status')
    update_player(player_id, new_name, new_mobile, new_age, new_sex, new_level, new_status)

    return redirect(referrer)


@app.route('/delete_player', methods=['POST','GET'])
def delete_player():

    referrer = request.referrer
    player_id = request.form.get('player_id')
    player = Players.objects(id = player_id).first()
    player.delete()

    return redirect(referrer)

@app.route('/contacts', methods=['POST','GET'])
def contacts():
    contacts = Contacts.objects()
    return render_template("chat_page.html",contacts = contacts)

@app.route('/message_history/<contact_id>', methods=['GET'])
def message_history(contact_id):
    messages = Message_db.objects(user_number=contact_id)
    message_list = []
    for message in messages:
        message_list.append({
            'message': message.message,
            'timestamp': message.created_at,
            'user_type': message.user_type
        })
    return jsonify(message_list)


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
            
            body = '''Welcome to our Pedal Match making virtual agent. Please select your choice from the below menu. Thanks.
1. Match Reservations
2. FAQ'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = "started"
            return "okay",200
        elif session.get('context') == "started":
            message_send = twilio_client.messages.create(
                    from_ = phone_number,
                    body=f"Hi {profile_name}, I am Haresh from Pedal Court. Right now it's in testing stage. We will update the chatbot shortly. Thank you!",
                    to= sender
                )
            body= f"Hi {profile_name}, I am Haresh from Pedal Court. Right now it's in testing stage. We will update the chatbot shortly. Thank you!"
            insert_into_message(sender[9:], body, "bot")
            session['context'] = None
            return "okay",200

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)