# config.py
import os
from datetime import datetime, timedelta


URL = "https://unityplace.aeroparker.com/book/Santander/Parking?parkingCmd=collectParkingDetails"

# User details for multiple vehicles
USER_DETAILS_LIST = [
    {
        "first_name": "Pankaj",
        "last_name": "Patel",
        "email": "pankaj.patel1@santander.co.uk",
        "vehicle_reg": "P4ANX",
    },
    {
        "first_name": "Johnny",
        "last_name": "Agbotui",
        "email": "johnny.agbotuijnr@santander.co.uk",
        "vehicle_reg": "ET67OMZ",
    },
        {
        "first_name": "Prakash",
        "last_name": "Parth",
        "email": "prakash.parth@santander.co.uk",
        "vehicle_reg": "PR13KAS",
    }
]

# Calculate tomorrow's date dynamically
current_datetime = datetime.now()
tomorrow_date = (current_datetime + timedelta(days=1)).strftime("%d/%m/%Y")

# Booking details
BOOKING_DETAILS = {
    "entry_date": tomorrow_date,
    "entry_time": "06:00",
    "exit_date": tomorrow_date,
    "exit_time": "19:00",
}



# If you need to install modules dynamically (not generally recommended in production):
# import subprocess
# def install_modules():
#     try:
#         import selenium  # Check if Selenium is installed
#     except ImportError:
#         print("Selenium not found. Installing...")
#         subprocess.check_call(["python", "-m", "pip", "install", "selenium"])

URL = "https://unityplace.aeroparker.com/book/Santander/Parking?parkingCmd=collectParkingDetails"

USER_DETAILS = {
    "first_name": "Pankaj",
    "last_name": "Patel",
    "email": "pankaj.patel1@santander.co.uk",  # Must be a valid building user email
    "contact": "1234567890",
    "vehicle_reg": "P4ANX"
}

# Original booking details with time-of-day, if needed
BOOKING_DETAILS = {
    "entry_date": "2025-01-17",  # YYYY-MM-DD format
    "entry_time": "06:00",       # HH:MM format
    "exit_date": "2025-01-17",   # YYYY-MM-DD format
    "exit_time": "19:00"         # HH:MM format
}

# For demonstration, we’re computing tomorrow’s date from a given "current_time"
# current_time = "2025-01-18T10:27:01Z"

# Get current local time
current_datetime = datetime.now()

# Get the current time as an ISO string
current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Convert to a datetime object
current_datetime = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%SZ")


current_datetime = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%SZ")
tomorrow_date = (current_datetime + timedelta(days=1)).date()

# Parking details for the actual form fields (dd/mm/yyyy)
# PARKING_DETAILS = {
#     "entry_date": tomorrow_date.strftime("%d/%m/%Y"),
#     "exit_date": tomorrow_date.strftime("%d/%m/%Y"),
# }

# Parking details for the actual form fields (dd/mm/yyyy)
PARKING_DETAILS = {
    "entry_date": tomorrow_date.strftime("%d/%m/%Y"),
    "entry_time": "06:00",  # Fixed entry time
    "exit_date": tomorrow_date.strftime("%d/%m/%Y"),
    "exit_time": "19:00",   # Default exit time
}


# If you want a dynamic approach using current system time, you can do:
# current_datetime = datetime.now()
# tomorrow_date = (current_datetime + timedelta(days=1)).date()
# PARKING_DETAILS = {
#     "entry_date": tomorrow_date.strftime("%d/%m/%Y"),
#     "exit_date": tomorrow_date.strftime("%d/%m/%Y"),
# }

# SSL check (optional)
def check_ssl_support():
    import ssl
    try:
        ssl.create_default_context()
        print("SSL module is available.")
    except Exception as e:
        raise RuntimeError("SSL module is missing or improperly configured.") from e

