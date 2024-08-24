from mongoengine import *
from datetime import datetime,timedelta
from utils import validate_input

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")


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
    state = StringField()  # Searching, Open, 
    created_at = DateTimeField()

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
    


def check_booking_exist(match_number):
    is_exist = Bookings.objects(match_number = match_number).first()
    if is_exist:
        return is_exist
    else:
        return None

# Fetch all_the bookings, in ascending order
def fetch_all_bookings():
    all_bookings = Bookings.objects()
    return all_bookings

# Number of Total Bookings
def get_numOfBookings():
    num_of_bookings = Bookings.objects.count()
    return num_of_bookings

# Number of unfinished Bookings
def get_numOfunfinishedBookings():
    num_of_bookings = Bookings.objects(state = "Searching").count()
    return num_of_bookings


# Fetch all bookings by a day
def fetch_all_bookings_by_date(date):
    all_bookings = Bookings.objects(booking_date = date)
    return all_bookings

# Fetch booking by id
def fetch_booking_by_id(id):
    exact_boooking = Bookings.objects(id = id).first()
    return exact_boooking

def is_time_conflict(existing_time, input_start_time, input_end_time):
    existing_start_time, existing_end_time = existing_time.split('-')
    existing_start_time = datetime.strptime(existing_start_time.strip(), "%H:%M")
    existing_end_time = datetime.strptime(existing_end_time.strip(), "%H:%M")
    input_start_time = datetime.strptime(input_start_time, "%H:%M")
    input_end_time = datetime.strptime(input_end_time, "%H:%M")

    return max(existing_start_time, input_start_time) < min(existing_end_time, input_end_time)

def check_availability(input_date, input_time_range, court_name):
    # Convert input date from DD-MM-YYYY to YYYY-MM-DD
    input_date = datetime.strptime(input_date, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    # Parse the input time range
    input_start_time, input_end_time = input_time_range.split('-')
    input_start_time = input_start_time.strip()
    input_end_time = input_end_time.strip()
    
    # Query the database for bookings on the same date
    existing_bookings = Bookings.objects(booking_date=input_date, court_name=court_name)

    for booking in existing_bookings:
        if is_time_conflict(booking.booking_time, input_start_time, input_end_time):
            print(f"Time conflict found with booking ID: {booking.id}")
            return False  # Time conflict found
    
    print("No time conflict, booking is available.")
    return True  # No time conflict