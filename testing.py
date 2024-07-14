
from datetime import datetime,timedelta

import pytz

# Define the timezone for Spain
spain_tz = pytz.timezone('Europe/Madrid')

# Get the current time in Spain
spain_time = datetime.now(spain_tz)

print(spain_time.strftime('%Y-%m-%d %H:%M:%S'))