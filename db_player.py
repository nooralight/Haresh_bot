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
    