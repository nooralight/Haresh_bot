from mongoengine import *
from datetime import datetime,timedelta

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

# Define the MongoDB document schema using mongoengine
class Bookings(Document):
    id = SequenceField(primary_key=True)
    booking_date = StringField()
    booking_time = StringField()
    court_name = StringField()
    match_number = StringField()
    player_count = IntField()
    player_occupied = IntField()
    players_name_list = ListField(StringField())
    state = StringField()
    created_at = DateTimeField()


all_bookings = Bookings.objects()

for item in all_bookings:
    if item.booking_time[1] == ":":
        item.booking_time = f"0{item.booking_time}"
        item.save()
        print("Saved")