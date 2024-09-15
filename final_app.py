from flask import Flask, request, jsonify,session, render_template, redirect, url_for
from flask_session import Session
from twilio.rest import Client
from mongoengine import *
from datetime import datetime,timedelta
import time, json
from db_player import add_new_player, update_player
from db_booking import check_booking_exist,insert_new_another_booking,fetch_all_bookings_by_date, fetch_booking_by_id, get_numOfBookings, get_numOfunfinishedBookings, check_availability
import pytz
import re
from gpt_functions import initiate_interaction, trigger_assistant, checkRunStatus, retrieveResponse, sendNewMessage_to_existing_thread
from utils import validate_date , validate_time_range
from db_invitations import create_new_invitation, send_message_to_matched_users,get_invitation_by_matchID
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
    last_invite_match = ListField()
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
                     "19:00-20:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
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
        "19:00-20:00": {"Pádel 1": None, "Pádel 2": None, "Pádel 3": None, "Pádel 4": None, "Pádel 5": None, "Pádel 6": None},
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
    new_hand = request.form.get('new_hand')
    new_position = request.form.get('new_position')
    update_player(player_id, new_name, new_mobile, new_age, new_sex, new_level, new_status, new_hand, new_position)

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
        if already_player.last_invite_match and len(already_player.last_invite_match)>0:
            if message == "Yes, confirm me":
                for item in already_player.last_invite_match:
                    booking = check_booking_exist(item['match_number'])
                    if booking.state == "Searching":
                        booking.players_name_list.append(already_player.name)
                        currently_player_count = booking.player_occupied
                        booking.player_occupied = currently_player_count+1
                        booking.save()
                        # Also check to change status
                        if booking.player_occupied == 4:
                            booking.state = "Open"
                            invitation = get_invitation_by_matchID(item['match_number'])
                            invitation.status = "closed"
                            booking.save()
                            invitation.save()
                        body = "Thank you for joining the match. You are registered into this match from now."
                        message_created = twilio_client.messages.create(
                            from_= phone_number,
                            body= body,
                            to= f"whatsapp:{already_player.mobile}"
                        )
                        insert_into_message(already_player.mobile, body, "bot")

                        already_player.last_invite_match = []
                        already_player.save()

                        
                    else:
                        body = '''Sorry the booking has already been closed. Thank you for showing interest'''
                        message_created = twilio_client.messages.create(
                            from_= phone_number,
                            body= body,
                            to= f"whatsapp:{already_player.mobile}"
                        )
                        insert_into_message(already_player.mobile, body, "bot")

                        already_player.last_invite_match = []
                        already_player.save()
                    
                    
                    
            elif message == "No, reject":
                body = '''Thank you for your response. You won't be invited for this match anymore.'''
                message_created = twilio_client.messages.create(
                    from_= phone_number,
                    body= body,
                    to= f"whatsapp:{already_player.mobile}"
                )
                insert_into_message(already_player.mobile, body, "bot")

                already_player.last_invite_match = []
                already_player.save()
                
            elif message == "Unsubscribe me":
                body = '''You have been unsubscribed from getting match invitations.'''
                message_created = twilio_client.messages.create(
                    from_= phone_number,
                    body= body,
                    to= f"whatsapp:{already_player.mobile}"
                )
                insert_into_message(already_player.mobile, body, "bot")

                already_player.last_invite_match = []
                already_player.status = "Stopped"
                already_player.save()
                
            else:
                for item in already_player.last_invite_match:
                    message_created = twilio_client.messages.create(
                            from_= messaging_sid, 
                            content_sid= "HXe9c3a08640af9c1c4c71f8dc78a913ca",
                            content_variables= json.dumps({
                                "1": already_player.name,
                                "2": item['match_number'],
                                "3": item['searched_hand'],
                                "4": item['searched_position'],
                                "5":already_player.level,
                                "6": item['total_timeline']
                            }),
                            to = f"whatsapp:{item.mobile}"
                        )
                    
                    return "okay", 200
                
        else:
            
            
            if session.get('context') == None or 'context' not in session:

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
                session['context'] = None
                return "okay",200
        
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)