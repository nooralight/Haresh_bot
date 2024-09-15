from mongoengine import *
from datetime import datetime

# Define the MongoDB connection
connect(host="mongodb://127.0.0.1:27017/haresh?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10")

class Invitations(Document):
    id = SequenceField(primary_key=True)
    match_id = IntField()
    created_by_player_id = IntField()
    created_by_player_name = StringField()
    searched_level = StringField()
    match_date = StringField()
    match_time_range = StringField()
    pedal = StringField()
    status = StringField(default = "searching") # Either "Searching" or closed
    last_sent = DateTimeField() # Because every 8 hours later, the invitation will be sent, 3 times a day
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
    last_invite_match = ListField()
    created_at = DateTimeField()
    updated_at = DateTimeField()



def create_new_invitation(match_id, player_id, player_name, match_date, match_time_range, pedal, searched_level):
    new_invitation = Invitations(
        match_id = match_id,
        created_by_player_id = player_id,
        created_by_player_name = player_name, 
        match_date = match_date,
        match_time_range = match_time_range,
        pedal = pedal,
        searched_level = searched_level,
        created_at = datetime.now()
    )
    new_invitation.save()
    return new_invitation

def send_message_to_matched_users(invitation_id):
    the_invitation = Invitations.objects(id = invitation_id).first()
    # Extract criteria from the invitation
    player_id = the_invitation.created_by_player_id
    searched_level = the_invitation.searched_level
    match_date = the_invitation.match_date
    match_time_range = the_invitation.match_time_range

    # Filter players based on the invitation criteria
    players = Players.objects(
        Q(level=searched_level.strip()) & # equal or +1
        Q(status = "Active") &
        Q(last_invite_match__size=0) &
        Q(mobile = "+8801301807991")
    )
    print(players.count())

    return players


def get_invitation_by_matchID(match_id):
    invitation = Invitations.objects(match_id = match_id).first()
    return invitation