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

# Fetch all_the bookings, in ascending order
def fetch_all_bookings():
    all_bookings = Match_booking.objects()
    return all_bookings

# Number of Total Bookings
def get_numOfBookings():
    num_of_bookings = Match_booking.objects().count()
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
    all_bookings = Match_booking.objects(booking_date = date)
    return all_bookings

