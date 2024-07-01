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
    age = IntField()
    sex = StringField()
    level = StringField()
    availability = StringField()
    preferred_position = StringField()
    dominant_hand = StringField()
    status = StringField()
    created_at = DateTimeField()
    updated_at = DateTimeField()


# Read the spreadsheet data using pandas
file_path = 'player_data.xlsx'  # Update with the correct file path if necessary
data = pd.read_excel(file_path)

# Process the data
def process_mobile(mobile):
    mobile = str(mobile)
    if len(mobile) == 9 and mobile.isdigit():
        return '+34 ' + mobile
    return mobile

def get_value_or_none(value):
    if pd.isna(value):
        return None
    return value

data['Mobile'] = data['Mobile'].apply(process_mobile)

# Upload data to MongoDB
for _, row in data.iterrows():
    player = Players(
        name=get_value_or_none(row['Cliente Contado - -']),
        mobile=get_value_or_none(row['Mobile']),
        age=get_value_or_none(row['Age']),
        sex=get_value_or_none(row['Sex']),
        level=get_value_or_none(row['Level']),
        availability=None,
        preferred_position=None,
        dominant_hand=None,
        status=None
    )
    player.save()