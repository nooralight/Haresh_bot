from flask import Flask, request, jsonify,session, render_template, redirect, url_for
from flask_session import Session
from twilio.rest import Client
from mongoengine import *
from datetime import datetime,timedelta
import time
from db_player import add_new_player, update_player
from db_booking import insert_new_booking, fetch_all_bookings_by_date, fetch_booking_by_id, get_numOfBookings, get_numOfunfinishedBookings
import pytz
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


@app.route('/', methods=['POST','GET'])
def home():
    numOfcontacts = Contacts.objects().count()
    numOfmessages = Message_db.objects().count()
    numOfplayers = Players.objects().count()
    numOfbookings = get_numOfBookings()
    numOfunfinished = get_numOfunfinishedBookings()
    return render_template("home.html", numOfcontacts = numOfcontacts, numOfmessages = numOfmessages, numOfplayers = numOfplayers, numOfbookings = numOfbookings, numOfunfinished= numOfunfinished)

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
        return render_template("bookings.html", t_date = date_str, booking_dict = booking_dict)
    else:
        for booking in today_bookings:
            booking_dict[booking.booking_time][booking.court_name]  = booking
    return render_template("bookings.html", t_date = date_str, booking_dict = booking_dict)

@app.route('/extra_bookings', methods=['POST','GET'])
def extra_bookings():
    # Define the timezone for Spain

    today_date = london_time
    date_str = today_date.strftime('%Y-%m-%d')

    today_bookings = fetch_all_bookings_by_date(date_str)
    
    booking_dict  = {"08:00-9:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "08:30-10:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "09:00-10:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "09:30-11:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "10:00-11:30":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "10:30-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
                     "11:00-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None,},
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
        return render_template("another_booking.html", t_date = date_str, booking_dict = booking_dict)
    else:
        for booking in today_bookings:
            booking_dict[booking.booking_time][booking.court_name]  = booking
    return render_template("another_booking.html", t_date = date_str, booking_dict = booking_dict)

@app.route('/bookings/<date_str>', methods=['POST', 'GET'])
def get_bookings_data_byDate(date_str):

    today_bookings = fetch_all_bookings_by_date(date_str)

    booking_dict  = {
        "08:00-9:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "08:30-10:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "09:00-10:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "09:30-11:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "10:00-11:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "10:30-12:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
        "11:00-12:00":{"Pádel 1":None,"Pádel 2":None,"Pádel 3":None,"Pádel 4":None,"Pádel 5":None,"Pádel 6":None},
        "11:00-12:30": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
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
    
    return render_template("another_booking.html", t_date = date_str, booking_dict = booking_dict)

@app.route('/check_booking/<id>', methods=['POST', 'GET'])
def check_booking(id):
    booking = fetch_booking_by_id(id)
    
    return render_template("booking_details.html", booking = booking)


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

    return render_template('players.html', players=players, pagination=pagination, total_pages = total_pages)


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
    print(message)
    # Checking if user already available
    already_user = Players.objects(mobile = sender[9:]).first()
    if not already_user:
        message_send = twilio_client.messages.create(
            from_= phone_number,
            body= "You are not a member of this padel community. Please register an account first through our management team",
            to= sender
        )
        return "okay", 200
    else:
        already_user.last_message = message
        already_user.save()
        if not already_user.availability  and not session.get('context') == "ask_availability":
            #available time
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HX7e7b31309eeef968224013f06deb12a9",
                    to = sender
                )
            
            body = '''Please tell us your available time for playing Pedal Matches. Choose the perfect timetable which is suitable for your availability.
1. 8 AM - 12:30 PM
2. 5 PM - 8 PM
3. 8 PM - 10 PM'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_availability'
            return "okay", 200
        
        elif not already_user.dominant_hand and not session.get('context') == "ask_dominant_hand" and not session.get('context') == "ask_availability":
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
        
        elif not already_user.preferred_position and not session.get('context') == "ask_preferred_position" and not session.get('context') == "ask_dominant_hand" and not session.get('context') == "ask_availability":
            #pref_pos
            message_send = twilio_client.messages.create(
                    from_= messaging_sid,
                    content_sid="HXc3849bee8ebdc174f14e1bdf13c29df0",
                    to = sender
                )
            
            body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player
3. Net Position
4. Baseline Position
5. Mixed Position'''
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
        message_send = twilio_client.messages.create(
                from_ = phone_number,
                body=f"Hi {profile_name}, I am Haresh from Pedal Court. Right now it's in testing stage. We will update the chatbot shortly. Thank you!",
                to= sender
            )
        body= f"Hi {profile_name}, I am Haresh from Pedal Court. Right now it's in testing stage. We will update the chatbot shortly. Thank you!"
        insert_into_message(sender[9:], body, "bot")
        session['context'] = None
        return "okay",200
    
    elif session.get('context') == "ask_availability":
        if message in ['8 AM - 12:30 PM', '5 PM - 8 PM', '8 PM - 10 PM']:
            if message == '8 AM - 12:30 PM':
                already_user.availability = '8 AM - 12:30 PM'
            elif message == '5 PM - 8 PM':
                already_user.availability = '5 PM - 8 PM'
            else:
                already_user.availability = '8 PM - 10 PM'
            already_user.save()
            
            ######  If preferred position is not given  ####
            if not already_user.preferred_position:

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
            
            elif not already_user.preferred_position:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing your availibility timetable.',
                    to = sender
                )
                insert_into_message(sender[9:], 'Thanks for providing your availibility timetable.', "bot")

                #pref_pos
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXc3849bee8ebdc174f14e1bdf13c29df0",
                        to = sender
                    )
                
                body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player
3. Net Position
4. Baseline Position
5. Mixed Position'''
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
                    content_sid="HX7e7b31309eeef968224013f06deb12a9",
                    to = sender
                )
            body = '''Please tell us your available time for playing Pedal Matches. Choose the perfect timetable which is suitable for your availability.
1. 8 AM - 12 PM
2. 5 PM - 8 PM
3. 8 PM - 10 PM'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_availability'
            return "okay", 200

    elif session.get('context') == "ask_dominant_hand":
        if message in ['Left hand', 'Right hand']:
            if message == 'Left hand':
                already_user.dominant_hand = 'Left hand'
                
            elif message == 'Right hand':
                already_user.dominant_hand = 'Right hand'

            already_user.save()
            if not already_user.preferred_position:

                first_message = twilio_client.messages.create(
                    from_= phone_number,
                    body= 'Thanks for providing info about your dominant hand.',
                    to= sender
                )
                insert_into_message(sender[9:], 'Thanks for providing info about your dominant hand.', "bot")

                #pref_pos
                message_send = twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid="HXc3849bee8ebdc174f14e1bdf13c29df0",
                        to = sender
                    )
                
                body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player
3. Net Position
4. Baseline Position
5. Mixed Position'''
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
        if message in ['Left Side Player', 'Right Side Player', 'Net Position', 'Baseline Position', 'Mixed Position']:
            already_user.preferred_position = message
            already_user.save()
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
                    content_sid="HXc3849bee8ebdc174f14e1bdf13c29df0",
                    to = sender
                )
            
            body = '''Please select the preferred position of your playing from the list.
1. Left Side Player
2. Right Side Player
3. Net Position
4. Baseline Position
5. Mixed Position'''
            insert_into_message(sender[9:], body, "bot")
            session['context'] = 'ask_preferred_position'
            return "okay", 200
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)