from mongoengine import *
from datetime import datetime,timedelta

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

# Define the MongoDB document schema using mongoengine
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


# Define the MongoDB document schema using mongoengine
class Bookings(Document):
    id = SequenceField(primary_key=True)
    booking_date = StringField()
    booking_time = StringField()
    court_name = StringField()
    match_number = StringField()
    match_level = StringField()
    player_count = IntField()
    player_occupied = IntField()
    players_name_list = ListField(StringField())
    state = StringField()
    created_at = DateTimeField()


# Create a new booking
def insert_new_booking(booking_date, booking_time, court_name, match_number, player_count, players_whatsapp_list, state):
    new_booking = Match_booking(
        booking_date = booking_date,
        booking_time = booking_time,
        court_name = court_name,
        match_number = match_number,
        player_count = player_count,
        players_whatsapp_list = players_whatsapp_list,
        state = state
    )
    new_booking.save()
    return new_booking  #Returning the newly created item

# Create a new booking
def insert_new_another_booking(booking_date, booking_time, court_name, match_number, match_level, player_count, player_occupied, players_name_list, state):
    new_booking = Bookings(
        booking_date = booking_date,
        booking_time = booking_time,
        court_name = court_name,
        match_number = match_number,
        match_level = match_level,
        player_count = player_count,
        player_occupied = player_occupied,
        players_name_list = players_name_list,
        state = state
    )
    new_booking.save()
    return new_booking  #Returning the newly created item

def update_another_booking(booking_id,booking_date, booking_time, court_name, match_number, match_level, player_count, player_occupied, players_name_list, state):
    the_booking = Bookings.objects(id = booking_id).first()

    the_booking.booking_date = booking_date
    the_booking.booking_time = booking_time
    the_booking.court_name = court_name
    the_booking.match_number = match_number
    the_booking.match_level = match_level
    the_booking.player_count = player_count
    the_booking.player_occupied = player_occupied
    the_booking.players_name_list = players_name_list
    the_booking.state = state
    the_booking.created_at = datetime.now()
    the_booking.save()
    print(f"Booking ID {booking_id} has been updated")


def check_booking_exist(match_number):
    is_exist = Bookings.objects(match_number = match_number).first()
    return is_exist

# Fetch all_the bookings, in ascending order
def fetch_all_bookings():
    all_bookings = Bookings.objects()
    return all_bookings

# Number of Total Bookings
def get_numOfBookings():
    num_of_bookings = Bookings.objects().count()
    return num_of_bookings

# Number of unfinished Bookings
def get_numOfunfinishedBookings():
    num_of_bookings = Bookings.objects(state = "Searching").count()
    return num_of_bookings

# insert new_player into an existing match
def insert_new_player_into_booking(booking_id, new_player_whatsapp):
    the_booking = Match_booking.objects(id=booking_id).first()
    if the_booking:
        the_booking.update(push__players_whatsapp_list=new_player_whatsapp)
        print(f"Player {new_player_whatsapp} added to booking ID {booking_id}")
    else:
        print(f"Booking with ID {booking_id} not found")


# Fetch all bookings by a day
def fetch_all_bookings_by_date(date):
    all_bookings = Bookings.objects(booking_date = date)
    return all_bookings

# Fetch booking by id
def fetch_booking_by_id(id):
    exact_boooking = Bookings.objects(id = id).first()
    return exact_boooking