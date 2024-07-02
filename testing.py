from mongoengine import *
import pandas as pd
from datetime import datetime

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

# Define the MongoDB document schema using mongoengine
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


all_players = Players.objects()
levels = []
for player in all_players:
    if player.level not in levels:
        levels.append(player.level)

print(levels)