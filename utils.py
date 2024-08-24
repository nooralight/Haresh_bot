import re
from datetime import datetime

def validate_date(input_date):
    """
    Validate the date input format (DD-MM-YYYY).
    """
    try:
        datetime.strptime(input_date, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def validate_time_range(input_time_range):
    """
    Validate the time range input format (HH:MM - HH:MM).
    """
    time_range_pattern = r"^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}$"
    if re.match(time_range_pattern, input_time_range):
        try:
            start_time, end_time = input_time_range.split('-')
            start_time = start_time.strip()
            end_time = end_time.strip()
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            return True
        except ValueError:
            return False
    return False

def validate_input(input_date, input_time_range):
    """
    Validate both date and time range inputs.
    """
    if not validate_date(input_date):
        print("Invalid date format. Please use DD-MM-YYYY.")
        return False
    
    if not validate_time_range(input_time_range):
        print("Invalid time range format. Please use HH:MM - HH:MM.")
        return False
    
    print("Input is valid.")
    return True

