import subprocess
from flask import Flask, request, redirect, session, url_for, render_template
from flask import Flask, request, redirect, url_for, render_template, Response
from flask import send_file
from HoursAdder import calculate_total_time  
import datetime
import re
import random
import string
import threading
import os
from flask import send_from_directory
import sys
import time
import csv

app = Flask(__name__)
app.secret_key = 'skywardsyntazx'
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
r_string = ("/" + random_string)
python_executable = sys.executable

# Implement a global dictionary to track the last request time for each client IP address.
client_cooldowns = {}
client_request_counts = {}

# Read version number from version.txt
with open('version.txt', 'r') as version_file:
    version_number = version_file.read().strip()

class Attendance:
    def __init__(self):
        # Read the data from attendanceBackup.txt
        with open('attendanceBackup.txt', 'r') as backup_file:
            backup_data = backup_file.read()

        # Write the backup data to attendance.txt
        with open('attendance.txt', 'w') as attendance_file:
            attendance_file.write(backup_data)
        
        self.records = {}
    def check_in(self, id):
        print(f"check_in called with id {id}")


        now = datetime.datetime.now()
        if id not in self.records or 'check_out_time' in self.records[id]:
            self.records[id] = {'check_in_time': now}
            if not os.path.exists('attendance.txt'):
                print("attendance.txt does not exist")
                open('attendance.txt', 'w').close()
            with open('attendance.txt', 'a') as f:
                f.write(f"{id} Checked In at {now}\n")
            subprocess.run([python_executable, 'attendanceBackup.py'])
            return "Checked In!"
    
        
        
        else:
            return "Already Checked In!"

    def check_in_event(self, id, event):
        print(f"check_in-event called with id {id} and event {event}")

        now = datetime.datetime.now()
        attendance_file = os.path.join(os.getcwd(), f'attendance-{event}.txt')
        print(f"attendance file: {attendance_file}")
        with open(attendance_file, 'a') as f:
            print("attendance_file: " + attendance_file + " opened")
            f.write(f"{id} Checked In at {now}\n")  # Use f-string for string formatting

        # Read the file's contents
        with open(attendance_file, 'r') as f:
            contents = f.read()
        print(f"Contents of {attendance_file}:\n{contents}")

        return "Checked In - Event!"



    def check_out(self, id):
        print(f"check_out called with id {id}")

        now = datetime.datetime.now()
        check_in_time = None
        if not os.path.exists('attendance.txt'):
            print("attendance.txt does not exist")
            open('attendance.txt', 'w').close()
        # Check if the user has an incomplete entry in the attendance.txt file
        with open('attendance.txt', 'r') as f:
            lines = f.readlines()
        # Check if the user has an incomplete entry in the attendance.txt file
        with open('attendance.txt', 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                check_in_time_str = line.split(" at ")[1].strip()
                check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
                break

        if check_in_time is not None or (id in self.records and 'check_in_time' in self.records[id]):
            if check_in_time is None:
                check_in_time = self.records[id]['check_in_time']
            time_diff = now - check_in_time

            # Convert time_diff from seconds to minutes and hours
            total_seconds = time_diff.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            self.records[id] = {'check_out_time': now}

            # Update the relevant line
            for i, line in reversed(list(enumerate(lines))):
                if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                    lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                    break

            # Write the updated content back to the file
            with open('attendance.txt', 'w') as f:
                print("attendance.txt exists")
                f.writelines(lines)

            subprocess.run([python_executable, 'attendanceBackup.py'])            
            return f"Checked Out! Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes"
        else:
            return "Not Checked In!"
        
    def check_out_event(self, id, event):
        print(f"check_out called with id {id}")

        now = datetime.datetime.now()
        check_in_time = None
        attendance_file = f'attendance-{event}.txt'
        if not os.path.exists(attendance_file):
            print(f"{attendance_file} does not exist")
            open(attendance_file, 'w').close()
        with open(attendance_file, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                check_in_time_str = line.split(" at ")[1].strip()
                check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
                break

        if check_in_time is not None or (id in self.records and 'check_in_time' in self.records[id]):
            if check_in_time is None:
                check_in_time = self.records[id]['check_in_time']
            time_diff = now - check_in_time

            # Convert time_diff from seconds to minutes and hours
            total_seconds = time_diff.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            self.records[id] = {'check_out_time': now}

            # Update the relevant line
            for i, line in reversed(list(enumerate(lines))):
                if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                    lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                    break

            # Write the updated content back to the file
            with open(attendance_file, 'w') as f:
                print("attendance.txt exists")
                f.writelines(lines)
        
            return f"Checked Out! Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes"
        else:
            return "Not Checked In!"

    def check_status_and_act(self, id):
        now = datetime.datetime.now()
        print(f"check_status_and_act called with id {id}")

        # Check if the user has an incomplete entry in the attendance.txt file
        with open('attendance.txt', 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                check_in_time_str = line.split(" at ")[1].strip()
                check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
                time_diff = now - check_in_time

                # Convert time_diff from seconds to minutes and hours
                total_seconds = time_diff.total_seconds()
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if hours >= 10:
                    # If it's been more than 10 hours, check them out and check them in again
                    lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                    with open('attendance.txt', 'w') as f:
                        f.writelines(lines)
                    return self.check_in(id)
                else:
                    return self.check_out(id)

        # If the user doesn't have an incomplete entry, proceed as before
        if id in self.records and 'check_in_time' in self.records[id] and 'check_out_time' not in self.records[id]:
            return self.check_out(id)
        else:
            return self.check_in(id) if re.match(r'^\d{6}$', id) else "Invalid Student Id Number. Please enter only the 6 digit number."

attendance = Attendance()  # Create an instance of Attendance

def check_client_cooldown(client_ip):
    current_time = time.time()
    if client_ip not in client_request_counts:
        client_request_counts[client_ip] = [current_time]
    else:
        client_request_counts[client_ip].append(current_time)
        client_request_counts[client_ip] = [t for t in client_request_counts[client_ip] if current_time - t <= 1]
        if len(client_request_counts[client_ip]) > 3:
            if client_ip not in client_cooldowns or current_time - client_cooldowns[client_ip] >= 10:
                client_cooldowns[client_ip] = current_time
                return True
    return False

@app.route('/raw_hours', methods=['GET'])
def attendance_data():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    with open('attendance.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')


@app.route('/total_hours', methods=['GET'])
def total_data():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    with open('hourTotals.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')

@app.route('/download_csv', methods=['GET'])
def download_file():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    subprocess.run([python_executable, 'sheetExporter.py'])
    return send_file('hourTotals.csv', as_attachment=True)

def read_login_credentials():
    with open('login.txt', 'r') as file:
        username = file.readline().strip()
        password = file.readline().strip()
    return username, password

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username, password = read_login_credentials()
        if request.form['username'] != username or request.form['password'] != password:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['username']
            return redirect('/' + random_string)
    return render_template('login.html', error=error, version=version_number)

@app.route('/volunteer+HASHSTRING', methods=['GET'])
def handle_volunteer():
    return redirect("/volunteer" + r_string)

@app.route('/' + random_string, methods=['GET', 'POST'])
def home():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    message = ''
    if request.method == 'POST':
        id = request.form.get('id')
        message = attendance.check_status_and_act(id)
    return render_template('home.html', message=message, version=version_number)


@app.route('/WestwoodRoboticsAdmin', methods=['GET'])
def admin():
    if 'username' in session and session['username'] == 'admin':
        return render_template('admin.html', version=version_number)
    else:
        session['next_url'] = url_for('admin')
        return redirect(url_for('admin_login'))

@app.route('/login', methods=['GET', 'POST'])
def loginz():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':
            session['username'] = username
            next_url = session.pop('next_url', url_for('home'))
            return redirect(next_url)
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error, version=version_number)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'secret':
            session['username'] = username
            next_url = session.pop('next_url', url_for('admin'))
            return redirect(next_url)
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('admin_login.html', error=error, version=version_number)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Add this new route to your Flask application
@app.route('/calculate_hours', methods=['GET'])
def calculate_hours():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    subprocess.run([python_executable, 'HoursAdder.py'])
    return redirect(url_for('admin'))

@app.route('/archive', methods=['GET'])
def archives():
    # Get the list of .txt files in the Archives folder
    archive_files = [file for file in os.listdir('Archives') if file.endswith('.txt')]
    if 'username' in session and session['username'] == 'admin':
        return render_template('archive.html', archive_files=archive_files, version=version_number)
    else:
        session['next_url'] = url_for('admin')
        return redirect(url_for('loginz'))



@app.route('/download/<filename>', methods=['GET'])
def download_archive(filename):
    # Construct the full file path by joining the 'Archives' folder and the selected filename
    file_path = os.path.join('Archives', filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return "File not found"

    # Return the file as an attachment
    return send_from_directory('Archives', filename, as_attachment=True)


@app.route('/reset_all', methods=['GET'])
def reset_all():
    if confirm_reset():
        clear_files()
        return redirect(url_for('admin'))
    else:
        return "Reset action canceled."

@app.route('/hours', methods=['GET'])
def hours():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    subprocess.run([python_executable, 'HoursAdder.py'])
    with open('hourTotals.txt', 'r') as f:
        data = f.read()
    return render_template('hours.html', data=data, version=version_number)

@app.route('/volunteer' + r_string, methods=['GET', 'POST'])
def volunteer():
    error = None
    if request.method == 'POST':
        inputUsername = request.form.get('username')  # Added to handle username input
        inputPassword = request.form.get('password')
        username, password = read_login_credentials()
        if inputUsername != username or inputPassword != password:  # Modified to check both username and password
            error = "Invalid Credentials. Please try again."
        else:
            return redirect('/volunteer-select' + r_string)
    return render_template('volunteer.html', error=error, version=version_number)  # Modify to include error handling

@app.route('/volunteer-select' + r_string, methods=['GET', 'POST'])
def volunteer_select():
    if request.method == 'POST':
        event = request.form.get('event')
        eventName = request.form.get('eventName')
        # Create a new file for each event
        with open(f'attendance-{event}.txt', 'w') as f:
            pass
        return redirect(url_for('volunteer_login', event=event, eventName=eventName))
    
    # Read events from event_list.txt
    with open('event_list.txt', 'r') as file:
        events = file.readlines()
    
    return render_template('volunteer_select.html', events=events, version=version_number)

@app.route('/volunteer-login' + r_string, methods=['GET', 'POST'])
def volunteer_login():
    message = ''
    eventName = request.args.get('eventName')
    event = request.args.get('event')  # Get the event value from the query string parameter
    if request.method == 'POST':
        id = request.form.get('id')


        print("volunteer login" + eventName + " id:" + id)
        # Use the event-specific attendance file
        attendance_file = f'attendance-{event}.txt'

        # Check if the user has an incomplete entry in the attendance file
        with open(attendance_file, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                # If the user has an incomplete entry, check them out
                message = attendance.check_out_event(id, event)
                break
        else:
            # If the user doesn't have an incomplete entry, check them in
            message = attendance.check_in_event(id, event)

    return render_template('volunteer_login.html', message=message, event=eventName, version=version_number)  # Modify to include event name in the template

@app.route('/<eventname>-hours' + r_string, methods=['GET'])
def event_hours(eventname):
    event_file = f'attendance-{eventname}.txt'
    event_totals_file = f'{eventname}-HourTotals.txt'
    volunteer_totals_file = 'VolunteerHourTotals.txt'

    # Initialize a dictionary to store the total hours for each volunteer
    event_totals = {}
    volunteer_totals = {}

    # Read the event-specific attendance file
    with open(event_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'(\d+)\sChecked In at (.+?) and Checked Out at (.+?), Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
            if match:
                id, check_in_time_str, check_out_time_str, hours_str, minutes_str = match.groups()

            hours = int(hours_str) if hours_str.isdigit() else 0
            minutes = int(minutes_str) if minutes_str.isdigit() else 0
            total_minutes = hours * 60 + minutes

            # Add the total minutes to the event_totals dictionary
            if id in event_totals:
                event_totals[id] += total_minutes
            else:
                event_totals[id] = total_minutes

    # Write the event_totals to the event_totals_file
    with open(event_totals_file, 'w') as f:
        for id, total_minutes in event_totals.items():
            hours, minutes = divmod(total_minutes, 60)
            f.write(f"{id} Total Time: {hours} hours {minutes} minutes\n")

    # If the volunteer_totals_file exists, read it and update the volunteer_totals dictionary
    if os.path.exists(volunteer_totals_file):
        with open(volunteer_totals_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                id, _, _, rest = line.split(None, 3)
                hours_str, _, minutes_str = rest.rsplit(None, 2)
                hours = int(hours_str) if hours_str.isdigit() else 0
                minutes = int(minutes_str) if minutes_str.isdigit() else 0
                total_minutes = hours * 60 + minutes

                # Add the total minutes to the volunteer_totals dictionary
                if id in volunteer_totals:
                    volunteer_totals[id] += total_minutes
                else:
                    volunteer_totals[id] = total_minutes

    # Update the volunteer_totals dictionary with the event_totals
    for id, total_minutes in event_totals.items():
        if id in volunteer_totals:
            volunteer_totals[id] += total_minutes
        else:
            volunteer_totals[id] = total_minutes

    # Write the updated volunteer_totals to the volunteer_totals_file
    with open(volunteer_totals_file, 'w') as f:
        for id, total_minutes in volunteer_totals.items():
            hours, minutes = divmod(total_minutes, 60)
            f.write(f"{id} Total Time: {hours} hours {minutes} minutes\n")
    
    with open(event_totals_file, 'r') as f:
        data = f.read()

    return render_template('event_hours.html', data=data, eventname=eventname, version=version_number)  # Modify to include event name in the template

def confirm_reset():
    # Implement your logic to confirm the reset action here
    # For example, you can check if the admin is logged in or prompt for a password
    # Return True if the reset action is confirmed, False otherwise
    return True

def clear_files():
    # Clear the contents of attendance.txt
    with open('attendance.txt', 'w') as f:
        f.truncate(0)

    # Clear the contents of hourTotals.txt
    with open('hourTotals.txt', 'w') as f:
        f.truncate(0)

    with open ('attendanceBackup.txt', 'w') as f:
        f.truncate(0)
    # Delete the hourTotals.csv file
    if os.path.exists('hourTotals.csv'):
        os.remove('hourTotals.csv')

@app.route('/cooldown', methods=['GET'])
def cooldown():
    return render_template('cooldown.html', version=version_number)
    
@app.route('/hour_report')
def hourReportRedirect():
    return redirect(url_for('hour_report'))

@app.route('/hour_report' + r_string, methods=['GET', 'POST'])
def hour_report():
    if request.method == 'POST':
        start_date = datetime.datetime.strptime(request.form.get('start_date'), "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(request.form.get('end_date'), "%Y-%m-%d").date()
        hour_total = int(request.form.get('hour_total'))
        student_ids = [id.strip() for id in request.form.get('student_ids').split(',')]

        # Initialize a dictionary to store the total hours for each student
        student_totals = {student_id: 0 for student_id in student_ids}

        # Read the archive file
        with open('archive.txt', 'r') as f:
            lines = f.readlines()

        for line in lines:
            match = re.match(r'(\d+)\sChecked In at (.+?) and Checked Out at (.+?), Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
            if match:
                student_id, check_in_str, check_out_str, hours_str, minutes_str = match.groups()
                check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d %H:%M:%S.%f")
                check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d %H:%M:%S.%f")
                hours = int(hours_str)
                minutes = int(minutes_str)

                # Check if the student_id is in the list and the date is within the range
                if student_id in student_ids and start_date <= check_in.date() <= end_date:
                    student_totals[student_id] += hours * 60 + minutes

        # Convert minutes to hours and check if they meet the hour_total
        for student_id in student_totals:
            total_hours = student_totals[student_id] // 60
            student_totals[student_id] = {'hours': total_hours, 'met_reqs': total_hours >= hour_total}

        # Generate the CSV file
        csv_filename = 'hour_report.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Student ID', 'Total Hours', 'Met Requirements']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for student_id, totals in student_totals.items():
                writer.writerow({'Student ID': student_id, 'Total Hours': totals['hours'], 'Met Requirements': totals['met_reqs']})

        return send_file(csv_filename, as_attachment=True)
    else:
        return render_template('hour_report.html', version=version_number, r_string = r_string)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()

