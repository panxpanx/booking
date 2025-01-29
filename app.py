from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json

app = Flask(__name__)

CONFIG_FILE = '/Users/admin/pip_install/config.py'
BOOKING_FILE = '/Users/admin/pip_install/booking_reference.txt'

# Load user details from config file
def load_user_details():
    with open(CONFIG_FILE, 'r') as file:
        content = file.read()
    exec_globals = {}
    exec(content, exec_globals)
    return exec_globals.get('USER_DETAILS_LIST', [])

# Save user details to config file
def save_user_details(user_details_list):
    with open(CONFIG_FILE, 'r') as file:
        content = file.readlines()

    start_index = next(i for i, line in enumerate(content) if line.strip().startswith("USER_DETAILS_LIST ="))
    end_index = start_index + 1
    while not content[end_index].strip() == ']':
        end_index += 1
    end_index += 1

    new_list = f"USER_DETAILS_LIST = {json.dumps(user_details_list, indent=4)}\n"
    content[start_index:end_index] = [new_list]

    with open(CONFIG_FILE, 'w') as file:
        file.writelines(content)

# Load today's bookings from the file
def get_bookings_today():
    today = datetime.now().strftime('%Y-%m-%d')
    bookings = []
    with open(BOOKING_FILE, 'r') as file:
        lines = file.readlines()

    current_booking = {}
    for line in lines:
        line = line.strip()
        if line.startswith("Booking Reference:"):
            if current_booking and current_booking.get("date") == today:
                bookings.append(current_booking)
                current_booking = {}
            current_booking["reference"] = line.split(":")[1].strip()
        elif line.startswith("Booking Date:"):
            booking_date = line.split(":")[1].strip()
            current_booking["date"] = booking_date
        elif line.startswith("BOOKED FOR"):
            current_booking["name"] = line.split("BOOKED FOR")[1].strip()

    if current_booking and current_booking.get("date") == today:
        bookings.append(current_booking)

    return bookings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_users', methods=['GET'])
def get_users():
    user_details = load_user_details()
    return jsonify(user_details)

@app.route('/get_users_today', methods=['GET'])
def get_users_today():
    today = datetime.now().strftime('%Y-%m-%d')
    user_details = load_user_details()
    users_today = [user for user in user_details if user.get('update_date', '').startswith(today)]
    return jsonify(users_today)

@app.route('/get_bookings_today', methods=['GET'])
def get_bookings_today_endpoint():
    bookings_today = get_bookings_today()
    return jsonify(bookings_today)

@app.route('/view_today_booking_file', methods=['GET'])
def view_today_booking_file():
    today = datetime.now().strftime('%Y-%m-%d')
    filtered_entries = []

    with open(BOOKING_FILE, 'r') as file:
        lines = file.readlines()

    entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith("BOOKED FOR"):
            entry["name"] = line.split("BOOKED FOR")[1].strip()
        elif line.startswith("Booking Reference:"):
            entry["reference"] = line.split(":")[1].strip()
        elif line.startswith("Booking Date:"):
            date = line.split(":")[1].strip()
            entry["date"] = date
            if date.startswith(today):
                filtered_entries.append(entry)
                entry = {}

    return jsonify({"content": filtered_entries})

@app.route('/update', methods=['POST'])
def update_user():
    data = request.json
    user_details = load_user_details()

    for user in user_details:
        if user['email'] == data['email']:
            user['Book'] = data['Book']
            user['update_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    else:
        data['update_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_details.append(data)

    save_user_details(user_details)
    return jsonify({"message": "User details updated successfully!"})

if __name__ == '__main__':
    app.run(host='10.180.1.21', port=5000, debug=True)
