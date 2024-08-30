from flask import Flask, request, jsonify,session, render_template, redirect, url_for
from flask_session import Session
from twilio.rest import Client
from mongoengine import *
from datetime import datetime,timedelta
import time, json
from db_player import add_new_player, update_player
from db_booking import insert_new_another_booking,fetch_all_bookings_by_date, fetch_booking_by_id, get_numOfBookings, get_numOfunfinishedBookings, check_availability
import pytz
import re
from gpt_functions import initiate_interaction, trigger_assistant, checkRunStatus, retrieveResponse, sendNewMessage_to_existing_thread
from utils import validate_date , validate_time_range
from db_invitations import create_new_invitation, send_message_to_matched_users
import os
from dotenv import load_dotenv
load_dotenv()

import random
import string
import time



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

ASSISTANT_ID = "asst_rlyXRePpNMxXYcCO7GK64jX4"

# Define the timezone for London
london_tz = pytz.timezone('Europe/London')

# Get the current time in London
london_time = datetime.now(london_tz)

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
    availability_session = StringField()
    availability_time = StringField()
    preferred_position = StringField()
    dominant_hand = StringField()
    status = StringField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

class Match_booking(Document):
    id = SequenceField(primary_key=True)
    booking_date = StringField()
    booking_time = StringField()
    court_name = StringField()
    match_number = StringField()
    player_count = IntField()
    players_whatsapp_list = ListField(StringField())
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

def generate_random_string(length):
    # Define the possible characters (uppercase, lowercase, and digits)
    characters = string.digits
    
    # Generate a random string of the specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string

def send_content_message(content_sid, to):
    message_created = twilio_client.messages.create(
        from_= messaging_sid,
        content_sid= content_sid,
        to= to
    )

def send_plain_message(body, to):
    message_created = twilio_client.messages.create(
        from_= messaging_sid,
        body= body,
        to= to
    )


@app.route('/', methods=['POST','GET'])
def home():
    numOfcontacts = Contacts.objects().count()
    numOfmessages = Message_db.objects().count()
    numOfplayers = Players.objects().count()
    numOfbookings = get_numOfBookings()
    numOfunfinished = get_numOfunfinishedBookings()
    return render_template("testing_index.html", numOfcontacts = numOfcontacts, numOfmessages = numOfmessages, numOfplayers = numOfplayers, numOfbookings = numOfbookings, numOfunfinished= numOfunfinished)

@app.route('/bookings', methods=['POST','GET'])
def bookings():
    # Define the timezone for Spain

    today_date = london_time
    date_str = today_date.strftime('%Y-%m-%d')

    today_bookings = fetch_all_bookings_by_date(date_str)
    
    booking_dict  = {"08:00-09:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "08:30-10:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "09:00-10:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "09:30-11:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "10:00-11:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "10:30-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "11:00-12:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "17:00-18:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "17:30-19:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "18:00-19:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "18:30-20:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "19:00-20:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "19:30-21:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "19:30-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:00-21:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:00-21:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:00-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:30-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,}}
    
    if today_bookings.count() == 0:
        return render_template("testing_booking.html", t_date = date_str, booking_dict = booking_dict)
    else:
        for booking in today_bookings:
            booking_dict[booking.booking_time][booking.court_name]  = booking
    return render_template("testing_booking.html", t_date = date_str, booking_dict = booking_dict)

@app.route('/extra_bookings', methods=['POST','GET'])
def extra_bookings():
    # Define the timezone for Spain

    today_date = london_time
    date_str = today_date.strftime('%Y-%m-%d')

    today_bookings = fetch_all_bookings_by_date(date_str)
    
    booking_dict  = {"08:00-9:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "08:30-10:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "09:00-10:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "09:30-10:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
                     "09:30-11:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "10:00-11:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "10:30-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "11:00-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "11:00-12:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "11:30-13:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "17:00-18:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "17:30-19:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "18:00-19:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "18:30-20:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "19:00-20:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "19:30-21:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "19:30-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:00-21:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:00-21:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:00-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "20:30-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,}}
    
    if today_bookings.count() == 0:
        return render_template("testing_booking.html", t_date = date_str, booking_dict = booking_dict)
    else:
        for booking in today_bookings:
            booking_dict[booking.booking_time][booking.court_name]  = booking
    return render_template("testing_booking.html", t_date = date_str, booking_dict = booking_dict)

@app.route('/bookings/<date_str>', methods=['POST', 'GET'])
def get_bookings_data_byDate(date_str):

    today_bookings = fetch_all_bookings_by_date(date_str)

    booking_dict  = {
        "08:00-9:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "08:30-10:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "09:00-10:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "09:30-10:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "09:30-11:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "10:00-11:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "10:30-12:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "11:00-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None},
        "11:00-12:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "11:30-13:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
        "17:00-18:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "17:30-19:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "18:00-19:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "18:30-20:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "19:00-20:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "19:30-21:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "19:30-22:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "20:00-21:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
        "20:00-21:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "20:00-22:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
        "20:30-22:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None}
    }

    if today_bookings:
        for booking in today_bookings:
            print(booking.booking_date)
            booking_dict[booking.booking_time][booking.court_name] = booking
    
    return render_template("testing_booking.html", t_date = date_str, booking_dict = booking_dict)

@app.route('/check_booking/<id>', methods=['POST', 'GET'])
def check_booking(id):
    booking = fetch_booking_by_id(id)
    
    return render_template("testing_booking_details.html", booking = booking)


# @app.route('/add_new_booking', methods=['POST','GET'])
# def add_new_booking():
#     if request.method == "POST":
#         event_date = request.form.get('event_date')
#         event_time = request.form.get('event_time')
#         event_court = request.form.get('event_court')
#         event_capacity = request.form.get('event_capacity')
#         event_state = request.form.get('event_state')
#         event_match_no = request.form.get('event_match_no')
#         players_whatsapp_list = request.form.getlist('player_whatsapp[]')
#         final_player_list = []
#         for item in players_whatsapp_list:
#             if item!= "":
#                 final_player_list.append(item)
#         insert_new_booking(event_date, event_time, event_court, event_match_no, event_capacity, final_player_list, event_state)

#         return redirect(url_for('bookings'))
#     return render_template("add_event.html")

# @app.route('/players', methods=['POST','GET'])
# def players():
#     players = Players.objects().order_by('-id')
#     return render_template("players.html", players = players)

@app.route('/players', defaults={'page': 1},methods=['GET','POST'])
@app.route('/players/page/<int:page>',methods=['GET','POST'])
def players(page):
    per_page = 80
    skip = (page - 1) * per_page
    players = Players.objects().skip(skip).limit(per_page)
    total_players = Players.objects.count()
    # Calculate the total pages
    total_pages = (total_players + per_page - 1) // per_page
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_players,
    }

    return render_template('testing_list_player.html', players=players, pagination=pagination, total_pages = total_pages)


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
    
    return render_template('testing_add_new.html')

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
    contact = Contacts.objects(whatsapp = sender[9:]).first()
    if not contact:
        contact = insert_into_contacts(profile_name, sender[9:])
    if media_url:
        insert_into_message(sender[9:], "media_message", "user")
    else:
        insert_into_message(sender[9:], message, "user")
    print(message)
    # Checking if user already available
    already_player = Players.objects(mobile = sender[9:]).first()
    if not already_player:
        message_send = twilio_client.messages.create(
            from_= phone_number,
            body= "You are not a member of this padel community. Please register an account first through our management team",
            to= sender
        )
        return "okay", 200
    else:
        if not already_player.availability_session and not session.get('context') == "ask_availability" and not session.get('context') == "evening_extra":
            #available time
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HX9f39dd347c8c1b75eeb4d35565fbe9b6",
                    to = sender
                )
            
            body = '''Please tell us your available time for playing Pedal Matches. Choose the perfect timetable which is suitable for your availability.
1. Morning
2. Evening'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_availability'
            return "okay", 200
        
        elif not already_player.dominant_hand and not session.get('context') == "ask_dominant_hand" and not session.get('context') == "ask_availability" and not session.get('context') == "evening_extra":
            #dominant hand
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HXdcde334dc5cd1476b5b1a4600b850b53",
                    to = sender
                )
            
            body = '''Please select which one is your dominant hand?
1. Left Hand
2. Right Hand'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_dominant_hand'
            return "okay", 200
        
        elif not already_player.preferred_position and not session.get('context') == "ask_preferred_position" and not session.get('context') == "ask_dominant_hand" and not session.get('context') == "ask_availability" and not session.get('context') == "evening_extra":
            #pref_pos
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HXe1f8691aa5ec2b8a9065d0734c388e78",
                    to = sender
                )
            
            body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_preferred_position'
            return "okay", 200
        
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
        if message in ["Match Reservations","FAQ"]:
            if message == "Match Reservations":
                
                ## Date input for match ##
                send_content_message("HXa393ea5fc23b1aea289f1a00d802de62", sender)  # timetable_event
                session['context'] = "timetable_event"
                return "okay",200
            
                ## END ##
            
            else:
                message_send = twilio_client.messages.create(
                    from_ = phone_number,
                    body=f"Ask any question of yours. To exit from FAQ, type *quit* or type *exit*",
                    to= sender
                )
                body= f"Ask any question of yours. To exit from FAQ, type quit or type exit"
                insert_into_message(sender[9:], body, "bot")
                session['context'] = "chatgpt"
                return "okay",200
        
        else:

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
        
    elif session.get('context') == "chatgpt":

        if message.lower() == "quit" or message.lower() == "exit":
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
        
        else:

            final_response = None

            if 'my_thread_id' not in session:
                my_thread_id = initiate_interaction(message)
                session['my_thread_id'] = my_thread_id
            else:
                my_thread_id = session.get('my_thread_id')
                sendNewMessage_to_existing_thread(my_thread_id, message)

            run = trigger_assistant(my_thread_id, ASSISTANT_ID)

            while True:
                run_status = checkRunStatus(my_thread_id , run.id)
                print(f"Run status: {run_status.status}")
                if run_status.status == "failed":
                    final_response = "No response now"
                    break
                elif run_status.status == "completed":
                    # Extract the bot's response
                    final_response = retrieveResponse(my_thread_id)
                    break
                time.sleep(1)
            

            # Regex pattern to match the reference
            pattern = r'【\d+:\d+†source】'

            # Replace the reference with an empty string
            cleaned_response = re.sub(pattern, '', final_response)

            body = cleaned_response

            message_created = twilio_client.messages.create(
                from_= phone_number,
                body= cleaned_response,
                to= sender
            )

            insert_into_message(sender[9:], body, "bot")
            session['context'] = "chatgpt"
            return "okay",200
    

    elif session.get("context") == "timetable_event":
        val_date = validate_date(message)
        if val_date:
            session["timetable_event"] = message

            send_content_message("HXd28e1486b292a7b2de33a35f737ffe7c", sender) # timeline_event

            session['context'] = "timeline_event"
            return "okay", 200
        else:
            body= "Wrong input"
            send_plain_message(body, sender)

            time.sleep(2)
            ## Date input for match ##
            send_content_message("HXa393ea5fc23b1aea289f1a00d802de62", sender)  # timetable_event

            session['context'] = "timetable_event"
            return "okay",200


    elif session.get("context") == "timeline_event":
        
        if message in ["08:00-9:30", "09:30-11:00", "11:00-12:30", "17:00-18:30", "18:30-20:00", "20:00-21:30"]:

            session['timeline_event'] = message

            send_content_message("HXc51f7b87cf7088412cba39559aaba34c", sender)

            session["context"] = "padel_court_event"
            return "okay", 200
            # session['timeline_event'] = message

            # send_content_message("HX4da1ef2ae45f9ff2f5764e3624c6a899", sender)

            # session['context'] = "hand_event"
            # return "okay", 200
        
        else:
            body= "Wrong input"
            send_plain_message(body, sender)

            time.sleep(2)

            send_content_message("HXd28e1486b292a7b2de33a35f737ffe7c", sender) # timeline_event

            session['context'] = "timeline_event"
            return "okay", 200
    
    elif session.get("context") == "padel_court_event":
        if message in ["Pádel 1","Pádel 2","Pádel 3","Pádel 4","Pádel 5"]:
            is_available = check_availability(session.get("timetable_event"), session.get("timeline_event"), message)
            if is_available:
                session['padel_court_event'] = message

                send_content_message("HX4da1ef2ae45f9ff2f5764e3624c6a899", sender)

                session['context'] = "hand_event"
                return "okay", 200
            else:
                send_content_message("HXcad8d3decc44313287a86d61e24e8f20", sender)

                session['context'] = "change_action"
                return "okay", 200
        
        else:
            body= "Wrong input"
            send_plain_message(body, sender)

            time.sleep(2)
            send_content_message("HXc51f7b87cf7088412cba39559aaba34c", sender)

            session["context"] = "padel_court_event"
            return "okay", 200
    
    elif session.get('context') == "change_action":


        if message == "Change Time":
            send_content_message("HXd28e1486b292a7b2de33a35f737ffe7c", sender) # timeline_event

            session['context'] = "timeline_event"
            session['changing'] = "okay"
            return "okay", 200
        elif message == "Change Date":
            ## Date input for match ##
            send_content_message("HXa393ea5fc23b1aea289f1a00d802de62", sender)  # timetable_event

            session['context'] = "timetable_event"
            session['changing'] = "okay"
            return "okay",200
        elif message == "Change Padel Court":
            send_content_message("HXc51f7b87cf7088412cba39559aaba34c", sender)

            session["context"] = "padel_court_event"
            session['changing'] = "okay"    # TODO
            return "okay", 200
        else:
            send_content_message("HXcad8d3decc44313287a86d61e24e8f20", sender)

            session['context'] = "change_action"
            return "okay", 200
    
    elif session.get("context") == "hand_event":
        if message in ["Right Hand Player", "Left Hand Player"]:
            session['hand_event'] = message
            send_content_message("HXe7eb1d6e61e60528b0983a3c8481795d", sender)

            session['context'] = "position_event"
            return "okay", 200
        else:
            body= "Wrong input"
            send_plain_message(body, sender)

            time.sleep(2)
            send_content_message("HX4da1ef2ae45f9ff2f5764e3624c6a899", sender)

            session["context"] = "hand_event"
            return "okay", 200

    elif session.get("context") == "position_event":
        if message in ["Right side player", "Left side player"]:
            session['position_event'] = message
            send_content_message("HX207a883979d099a7b93d7d55a91ee565", sender) 

            session['context'] = "specific_player"
            return "okay", 200
        else:
            body= "Wrong input"
            send_plain_message(body, sender)

            time.sleep(2)
            send_content_message("HXe7eb1d6e61e60528b0983a3c8481795d", sender)

            session["context"] = "position_event"
            return "okay", 200
        
    elif session.get("context") == "specific_player":
        if message in ["Yes", "No"]:
            if message == "No":
                # TODO
                random_number = generate_random_string(4)
                match_number = f"{random_number}{get_numOfBookings()}"
                formatted_date = datetime.strptime(session.get("timetable_event"), "%d-%m-%Y").strftime("%Y-%m-%d")
                new_booking = insert_new_another_booking(formatted_date, session.get("timeline_event"), session.get("padel_court_event"), match_number, already_player.level, 4, 1,[already_player.name],"Searching")
                body = f"Match number *{match_number}* has been opened. Invitation request has been sent to player based on your choices that you have given."
                send_plain_message(body, sender)
                insert_into_message(already_player.mobile, body, "bot")
                # Create invitation in the database
                invitation_create = create_new_invitation(match_number, already_player.id, already_player.name, session.get('hand_event'),session.get('position_event'), formatted_date, session.get("timeline_event"),session.get("padel_court_event"))
                invitation_sending_players = send_message_to_matched_users(invitation_create.id)
                if invitation_sending_players.count()>0:
                    for item in invitation_sending_players:
                        try:
                            total_timeline = f"{formatted_date} , {session.get("timeline_event")}"
                            message_created = twilio_client.messages.create(
                                from_= messaging_sid, 
                                content_sid= "HXe9c3a08640af9c1c4c71f8dc78a913ca",
                                content_variables= json.dumps({
                                    "1": already_player.name,
                                    "2": match_number,
                                    "3": session.get('hand_event'),
                                    "4": session.get('position_event'),
                                    "5":already_player.level,
                                    "6": total_timeline
                                }),
                                to = item.mobile
                            )
                        except:
                            print("error message sending for ", item.mobile)

                session['context'] = None
                return "okay", 200
            elif message == "Yes":
                pass
        else:
            body= "Wrong input"
            send_plain_message(body, sender)

            time.sleep(2)
            send_content_message("HX207a883979d099a7b93d7d55a91ee565", sender) 

            session['context'] = "specific_player"
            return "okay", 200
                
    
    # First One

    elif session.get('context') == "ask_availability":
        if message in ['Morning', 'Evening']:
            if message == 'Morning':
                already_player.availability_session = 'Morning'
                already_player.availability_time = "08:00 - 12:30"
            elif message == 'Evening':
                message_created = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid= "HXa2a7e2453ee63195ffb0666832918996",
                    to= sender
                )
                session['evening_time'] = "yes"
                session['context'] = "evening_extra"
                already_player.availability_session = message
                body = '''In the evening, in which time range you are available?'''
                insert_into_message(sender[9:], body, "bot")
                return "okay", 200
            already_player.save()
            
            ######  If preferred position is not given  ####
            if not already_player.preferred_position:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to= sender
                )
                time.sleep(1)
                #dominant hand
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXdcde334dc5cd1476b5b1a4600b850b53",
                        to = sender
                    )
                
                body = '''Please select which one is your dominant hand?
1. Left Hand
2. Right Hand'''
                insert_into_message(sender[9:], body, "bot")
                session['context'] = 'ask_dominant_hand'
                return "okay", 200
            
            elif not already_player.preferred_position:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to = sender
                )
                insert_into_message(sender[9:], 'Thanks for providing your availibility timetable.', "bot")

                #pref_pos
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXe1f8691aa5ec2b8a9065d0734c388e78",
                        to = sender
                    )
                
                body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player'''
                insert_into_message(sender[9:], body, "bot")
                session['context'] = 'ask_preferred_position'
                return "okay", 200
            
            else:
                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to= sender
                )
                insert_into_message(sender[9:], 'Thanks for providing your availibility timetable.', "bot")

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
        else:
            message_created = twilio_client.messages.create(
                from_= messaging_sid,
                content_sid= "HXa2a7e2453ee63195ffb0666832918996",
                to= sender
            )
            body = '''In the evening, in which time range you are available?'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = "evening_extra"
            return "okay", 200

    ## First one done


    ## Second One

    elif session.get('context') == "evening_extra":
        if message in ['17:00 - 20:00', '20:00 - 22:00','All Evening']:
            already_player.availability_time =message
            already_player.save()
            
            ######  If preferred position is not given  ####
            if not already_player.dominant_hand:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to= sender
                )
                time.sleep(1)
                #dominant hand
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXdcde334dc5cd1476b5b1a4600b850b53",
                        to = sender
                    )
                
                body = '''Please select which one is your dominant hand?
1. Left Hand
2. Right Hand'''
                insert_into_message(sender[9:], body, "bot")
                session['context'] = 'ask_dominant_hand'
                return "okay", 200
            
            elif not already_player.preferred_position:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to = sender
                )
                insert_into_message(sender[9:], 'Thanks for providing your availibility timetable.', "bot")

                #pref_pos
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXe1f8691aa5ec2b8a9065d0734c388e78",
                        to = sender
                    )
                
                body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player'''
                insert_into_message(sender[9:], body, "bot")
                session['context'] = 'ask_preferred_position'
                return "okay", 200
            
            else:
                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to= sender
                )
                insert_into_message(sender[9:], 'Thanks for providing your availibility timetable.', "bot")

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
        else:
            #available time
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HX9f39dd347c8c1b75eeb4d35565fbe9b6",
                    to = sender
                )
            body = '''Please tell us your available time for playing Pedal Matches. Choose the perfect timetable which is suitable for your availability.
1. Morning
2. Evening'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_availability'
            return "okay", 200

    elif session.get('context') == "ask_dominant_hand":
        if message in ['Left hand', 'Right hand']:
            if message == 'Left hand':
                already_player.dominant_hand = 'Left hand'
                
            elif message == 'Right hand':
                already_player.dominant_hand = 'Right hand'

            already_player.save()
            if not already_player.preferred_position:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing info about your dominant hand.',
                    to= sender
                )
                insert_into_message(sender[9:], 'Thanks for providing info about your dominant hand.', "bot")

                #pref_pos
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXe1f8691aa5ec2b8a9065d0734c388e78",
                        to = sender
                    )
                
                body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player'''
                insert_into_message(sender[9:], body, "bot")
                session['context'] = 'ask_preferred_position'
                return "okay", 200
            
            else:
                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing info about your dominant hand.',
                    to= sender
                )
                insert_into_message(sender[9:], 'Thanks for providing info about your dominant hand.', "bot")

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

        else:
            #dominant hand
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HXdcde334dc5cd1476b5b1a4600b850b53",
                    to = sender
                )
            
            body = '''Please select which one is your dominant hand?
1. Left Hand
2. Right Hand'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_dominant_hand'
            return "okay", 200
        
    elif session.get('context') == "ask_preferred_position":
        if message in ['Left Side Player', 'Right Side Player']:
            already_player.preferred_position = message
            already_player.save()
            first_message = twilio_client.messages.create(
                from_= phone_number,
                body= 'Thanks for providing info about your preferred position.',
                to= sender
            )
            insert_into_message(sender[9:], 'Thanks for providing info about your preferred position.', "bot")

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
        else:
            #pref_pos
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HXe1f8691aa5ec2b8a9065d0734c388e78",
                    to = sender
                )
            
            body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player'''

            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_preferred_position'
            return "okay", 200
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)