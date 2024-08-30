from mongoengine import *
from datetime import datetime

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

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

def add_new_player(name, mobile, age, sex, level, status):
    new_player = Players(
        name = name,
        mobile = mobile,
        age = age,
        sex = sex,
        level = level,
        status = status,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )
    new_player.save()
    print(f"New Player created, Name: {name}")

def update_player(player_id, new_name, new_mobile, new_age, new_sex, new_level, new_status, new_hand, new_position):

    # Getting the Player object
    the_player = Players.objects(id = player_id).first()

    the_player.name = new_name
    the_player.mobile = new_mobile
    the_player.age = new_age
    the_player.sex = new_sex
    the_player.level = new_level
    the_player.status = new_status
    the_player.dominant_hand = new_hand
    the_player.preferred_position = new_position
    the_player.updated_at = datetime.now()
    the_player.save()

    print(f"Player ID:{player_id} has been updated")

def get_players_based_on_query(query_string):
    players = Players.objects(query_string)
    return players

    