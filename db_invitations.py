from mongoengine import *
from datetime import datetime

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

class Invitations(Document):
    id = SequenceField(primary_key=True)
    match_id = IntField()
    created_by_player_id = IntField()
    created_by_player_name = StringField()
    searched_hand = StringField()
    searched_position = StringField()
    searched_level = StringField()
    match_date = StringField()
    match_time_range = StringField()
    pedal = StringField()
    status = StringField(default = "searching") # Either "Searching" or closed
    last_sent = DateTimeField() # Becayse every 6 hours later, the invitation will be sent, 4 times a day
    created_at = DateTimeField()

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
    latest_invitation = DictField()
    created_at = DateTimeField()
    updated_at = DateTimeField()



def create_new_invitation(match_id, player_id, player_name, searched_hand, searched_position, match_date, match_time_range, pedal):
    new_invitation = Invitations(
        match_id = match_id,
        created_by_player_id = player_id,
        created_by_player_name = player_name, 
        searched_hand = searched_hand, 
        searched_position = searched_position,
        match_date = match_date,
        match_time_range = match_time_range,
        pedal = pedal,
        created_at = datetime.now()
    )
    new_invitation.save()
    return new_invitation

def send_message_to_matched_users(invitation_id):
    the_invitation = Invitations.objects(id = invitation_id).first()
    # Extract criteria from the invitation
    searched_hand = the_invitation.searched_hand
    searched_position = the_invitation.searched_position
    searched_level = the_invitation.searched_level
    match_date = the_invitation.match_date
    match_time_range = the_invitation.match_time_range

    # Filter players based on the invitation criteria
    players = Players.objects(
        Q(dominant_hand=searched_hand) &
        Q(preferred_position=searched_position) &
        Q(level=searched_level) &
        Q(mobile = "+8801301807991") &
        Q(status = "Active")
    )

    return players

    