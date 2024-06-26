import subprocess
from flask import Flask, request, redirect, session, url_for, render_template
from flask import Flask, request, redirect, url_for, render_template, Response
from flask import send_file
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
import json
import shutil

app = Flask(__name__)
app.secret_key = 'skywardsyntazx'
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
r_string = ("/" + random_string)
python_executable = sys.executable

client_cooldowns = {}
client_request_counts = {}

with open('data/version.txt', 'r') as version_file:
    version_number = version_file.read().strip()

recent_events = ["", "", ""]

id_validation_enabled = False

class Attendance:
    def __init__(self):
        self.records = {}
        attendance_file = 'data/rawHours/attendance.txt' 
        if not os.path.exists(attendance_file):
            open(attendance_file, 'w').close() 

    def check_in_out(self, id, event=None, action=None):
        global recent_events

        now = datetime.datetime.now() - datetime.timedelta(hours=5)
        attendance_file = 'data/rawHours/attendance.txt' if event is None else f'data/eventRawHours/attendance-{event}.txt'
        action_str = "Checked In" if action == "check_in" else "Checked Out"
        opposite_action_str = "Checked Out" if action == "check_in" else "Checked In"

        if not os.path.exists(attendance_file):
            open(attendance_file, 'w').close()

        with open(attendance_file, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{id} {opposite_action_str}") and action_str not in line:
                check_in_time_str = line.split(" at ")[1].strip()
                check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
                break
        else:
            check_in_time = now

        if action == "check_in":
            with open(attendance_file, 'a') as f:
                f.write(f"{id} Checked In at {now.strftime('%Y-%m-%d %H:%M:%S.%f')}\n")
        else:
            time_diff = now - check_in_time
            total_seconds = time_diff.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            for i, line in reversed(list(enumerate(lines))):
                if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                    lines[i] = f"{id} Checked In at {check_in_time.strftime('%Y-%m-%d %H:%M:%S.%f')} and Checked Out at {now.strftime('%Y-%m-%d %H:%M:%S.%f')}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                    break
            with open(attendance_file, 'w') as f:
                f.writelines(lines)

        recent_events.append(f"{id} - {action_str}")
        recent_events = recent_events[-3:]
        return f"{action_str}! Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes" if action == "check_out" else f"{action_str}!"

    def check_status_and_act(self, id, event=None):
        if not validate_student_id(id):
            return "Invalid Student ID. Please try again."
        now = datetime.datetime.now()

        attendance_file = 'data/rawHours/attendance.txt' if event is None else f'data/eventRawHours/attendance-{event}.txt'
        if not os.path.exists(attendance_file):
            open(attendance_file, 'w').close()

        with open(attendance_file, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
                return self.check_in_out(id, event, "check_out")

        return self.check_in_out(id, event, "check_in")
    
    def correct_hours(self, student_id, date_of_correction, hours_option, file_selection):
        if hours_option == "add_hours":
            hours_to_add = int(request.form.get('hours_to_add'))
            minutes_to_add = int(request.form.get('minutes_to_add'))

            self.add_hours(student_id, date_of_correction, hours_to_add, minutes_to_add, file_selection)
        elif hours_option == "check_in_out":
            check_in_time = request.form.get('check_in_time')
            check_out_time = request.form.get('check_out_time')

            self.add_check_in_out(student_id, date_of_correction, check_in_time, check_out_time, file_selection)
        elif hours_option == "exclusive_check_in_out": 
            check_in_time = request.form.get('check_in_time')
            check_out_time = request.form.get('check_out_time')

            self.add_exclusive_check_in_out(student_id, date_of_correction, check_in_time, check_out_time, file_selection)

    def add_hours(self, student_id, date_of_correction, hours_to_add, minutes_to_add, file_selection):
        for filename in file_selection:
            file_path = os.path.join("data", filename)
            with open(file_path, "r+") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith(f"{student_id} Checked In") and str(date_of_correction) in line and "Checked Out" not in line:
                        del lines[i]
                        lines = [line for line in lines if line.strip()]
                        break  
                found = False
                for i, line in enumerate(lines):
                    if student_id in line and str(date_of_correction) in line:
                        match = re.search(r"Meeting Time Recorded: (\d+) hours (\d+) minutes", line)
                        if match:
                            current_hours = int(match.group(1))
                            current_minutes = int(match.group(2))
                            total_minutes = (current_hours * 60 + current_minutes) + (
                                    hours_to_add * 60 + minutes_to_add
                            )
                            new_hours = total_minutes // 60
                            new_minutes = total_minutes % 60
                            lines[i] = line.replace(
                                match.group(0),
                                f"Meeting Time Recorded: {new_hours} hours {new_minutes} minutes",
                            )
                            found = True
                            break
                if not found:
                    check_in_time = datetime.datetime.strptime(f"{date_of_correction} 00:00:00.000000", "%Y-%m-%d %H:%M:%S.%f") 
                    check_out_time = check_in_time + datetime.timedelta(hours=hours_to_add, minutes=minutes_to_add)
                    check_out_time_str = check_out_time.strftime("%Y-%m-%d %H:%M:%S.%f") 
                    lines.append(
                        f"{student_id} Checked In at {check_in_time.strftime('%Y-%m-%d %H:%M:%S.%f')} and Checked Out at {check_out_time_str}, Meeting Time Recorded: {hours_to_add} hours {minutes_to_add} minutes\n"
                    )
                
                
                f.seek(0)
                f.writelines(lines)
                f.truncate()

    def add_check_in_out(self, student_id, date_of_correction, check_in_time, check_out_time, file_selection):
        for filename in file_selection:
            file_path = os.path.join("data", filename)
            check_in_datetime = datetime.datetime.strptime(f"{date_of_correction} {check_in_time}", "%Y-%m-%d %H:%M")
            check_out_datetime = datetime.datetime.strptime(f"{date_of_correction} {check_out_time}", "%Y-%m-%d %H:%M")

            time_diff = check_out_datetime - check_in_datetime
            total_seconds = time_diff.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            with open(file_path, "r+") as f:
                lines = f.readlines()
                f.seek(0) 
                f.truncate(0) 

                line_deleted = False

                for i, line in enumerate(lines):
                    if line.startswith(f"{student_id} Checked In") and str(date_of_correction) in line and "Checked Out" not in line:
                        line_deleted = True
                    else:
                        f.write(line)  

                    if line_deleted:
                        f.writelines(lines[i+1:])
                        break 

            with open(file_path, "a") as f:
                f.write(
                    f"{student_id} Checked In at {check_in_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')} and Checked Out at {check_out_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                )
    
    def add_exclusive_check_in_out(self, student_id, date_of_correction, check_in_time, check_out_time, file_selection):
        for filename in file_selection:
            file_path = os.path.join("data", filename)

            with open(file_path, "r+") as f:
                lines = f.readlines()
                f.seek(0)
                f.truncate(0)

                check_in_found = False
                for i, line in enumerate(lines):
                    if line.startswith(f"{student_id} Checked In") and str(date_of_correction) in line and "Checked Out" not in line:
                        check_in_found = True
                        check_in_time_str = line.split(" at ")[1].strip() 
                        check_in_datetime = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f") 
                        continue
                    f.write(line)

                if not check_in_found:
                    return "Error: No existing check-in found for this student and date."  

                check_out_datetime = datetime.datetime.strptime(f"{date_of_correction} {check_out_time}", "%Y-%m-%d %H:%M")

                time_diff = check_out_datetime - check_in_datetime
                total_seconds = time_diff.total_seconds()
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                f.write(
                    f"{student_id} Checked In at {check_in_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')} and Checked Out at {check_out_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                )


attendance = Attendance() 

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
    with open('data/rawHours/attendance.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')


@app.route('/total_hours', methods=['GET'])
def total_data():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    with open('data/totalHours/hourTotals.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')

@app.route('/download_csv', methods=['GET'])
def download_file():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    subprocess.run([python_executable, 'scripts/sheetExporter.py'])
    return send_file('data/totalHours/hourTotals.csv', as_attachment=True)

def read_login_credentials():
    with open('data/login.txt', 'r') as file:
        username = file.readline().strip()
        password = file.readline().strip()
    return username, password

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
    return render_template('home.html', message=message, version=version_number, recent_events=recent_events)


@app.route('/WestwoodRoboticsAdmin', methods=['GET'])
def admin():
    with open('data/id_validation_state.txt', 'r') as f:
        id_validation_enabled = f.read().strip().lower() == 'true'
    global random_string
    if 'username' in session and session['username'] == 'admin':
        return render_template('admin.html', version=version_number, recent_events=recent_events, id_validation_enabled=id_validation_enabled, r_string=r_string, random_string = random_string)
    else:
        session['next_url'] = url_for('admin')
        return redirect(url_for('admin_login'))

@app.route('/', methods=['GET', 'POST'])
def loginz():
    error = None
    if request.method == 'POST':
        username, password = read_login_credentials()
        input_username = request.form.get('username')
        input_password = request.form.get('password')
        if input_username == username and input_password == password:
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
    return redirect(url_for('loginz'))

@app.route('/calculate_hours', methods=['GET'])
def calculate_hours():
    client_ip = request.remote_addr
    if check_client_cooldown(client_ip):
        return redirect(url_for('cooldown'))
    subprocess.run([python_executable, 'scripts/HoursAdder.py'])
    return redirect(url_for('admin'))

@app.route('/archive', methods=['GET'])
def archives():
    archive_files = [file for file in os.listdir('Archives') if file.endswith('.txt')]
    if 'username' in session and session['username'] == 'admin':
        return render_template('archive.html', archive_files=archive_files, version=version_number)
    else:
        session['next_url'] = url_for('admin')
        return redirect(url_for('loginz'))



@app.route('/download/<filename>', methods=['GET'])
def download_archive(filename):
    file_path = os.path.join('Archives', filename)

    if not os.path.exists(file_path):
        return "File not found"

    return send_from_directory('Archives', filename, as_attachment=True)


def archive_attendance_files():
    archive_root_dir = 'Archives'
    if not os.path.exists(archive_root_dir):
        os.makedirs(archive_root_dir)

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.datetime.now().strftime('%H-%M-%S')
    date_dir = os.path.join(archive_root_dir, f'Archive-{current_date}')
    datetime_dir = os.path.join(date_dir, f'Archive-{current_date}-{current_time}')

    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
    if not os.path.exists(datetime_dir):
        os.makedirs(datetime_dir)

    data_dir = 'data'
    for file in os.listdir(data_dir):
        if file.startswith('attendance') or file == 'event_list.txt':
            shutil.copy(os.path.join(data_dir, file), datetime_dir)

@app.route('/archive_all', methods=['GET'])
def archive_all():
    calculate_hours()
    archive_attendance_files()
    return redirect(url_for('admin'))

@app.route('/volunteer' + r_string, methods=['GET', 'POST'])
def volunteer():
    error = None
    if request.method == 'POST':
        inputUsername = request.form.get('username') 
        inputPassword = request.form.get('password')
        username, password = read_login_credentials()
        if inputUsername != username or inputPassword != password: 
            error = "Invalid Credentials. Please try again."
        else:
            return redirect('/volunteer-select' + r_string)
    return render_template('volunteer.html', error=error, version=version_number)  

@app.route('/volunteer-select' + r_string, methods=['GET', 'POST'])
def volunteer_select():
    if request.method == 'POST':
        event = request.form.get('event')
        eventName = request.form.get('eventName')
        try:
            with open(f'data/eventRawHours/attendance-{event}.txt', 'x') as f:
                pass 
        except FileExistsError:
            pass 
        return redirect(url_for('volunteer_login', event=event, eventName=eventName))
    
    with open('data/event_list.txt', 'r') as file:
        events = file.readlines()
    
    return render_template('volunteer_select.html', events=events, version=version_number)

@app.route('/volunteer-login' + r_string, methods=['GET', 'POST'])
def volunteer_login():
    message = ''
    eventName = request.args.get('eventName')
    event = request.args.get('event') 
    if request.method == 'POST':
        id = request.form.get('id')

        attendance_file = f'data/eventRawHours/attendance-{event}.txt'
        message = attendance.check_status_and_act(id, event)

    return render_template('volunteer_login.html', message=message, event=eventName, version=version_number, recent_events=recent_events) 

@app.route('/<eventname>-hours' + r_string, methods=['GET'])
def event_hours(eventname):
    event_file = f'data/eventRawHours/attendance-{eventname}.txt'
    event_totals_file = f'data/eventTotalHours/{eventname}-HourTotals.txt'

    event_totals = {}

    with open(event_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'(\d+)\sChecked In at (.+?) and Checked Out at (.+?), Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
            if match:
                id, check_in_time_str, check_out_time_str, hours_str, minutes_str = match.groups()

            hours = int(hours_str) if hours_str.isdigit() else 0
            minutes = int(minutes_str) if minutes_str.isdigit() else 0
            total_minutes = hours * 60 + minutes

            if id in event_totals:
                event_totals[id] += total_minutes
            else:
                event_totals[id] = total_minutes

    # Get event name, outreach factor, and cap from event_list.txt
    with open('data/event_list.txt', 'r') as f:
        for line in f:
            event_code, event_name, outreach_scale_factor, outreach_hour_cap = line.strip().split(' | ')
            if event_code == eventname:
                outreach_scale_factor = float(outreach_scale_factor)
                outreach_hour_cap = float(outreach_hour_cap)
                break
        else:
            outreach_scale_factor = 1.0
            outreach_hour_cap = float('inf')  # No cap if not found
            event_name = eventname # Use event code as name if not found

    event_outreach_hours = {}
    with open(event_totals_file, 'w') as f:
        for id, total_minutes in event_totals.items():
            hours, minutes = divmod(total_minutes, 60)
            total_event_hours = total_minutes / 60
            outreach_hours = min(round(total_event_hours * outreach_scale_factor, 2), outreach_hour_cap)
            
            # Calculate outreach hours in hours and minutes
            outreach_hours_int = int(outreach_hours)
            outreach_minutes = int(round((outreach_hours - outreach_hours_int) * 60))

            event_outreach_hours[id] = f"{outreach_hours_int} hours {outreach_minutes} minutes"
            f.write(f"{id} | {hours} hours {minutes} minutes | {outreach_hours_int} hours {outreach_minutes} minutes\n") 

    with open(event_totals_file, 'r') as f:
        data = f.read()

    return render_template('event_hours.html', data=data, eventname=eventname, version=version_number, event_outreach_hours=event_outreach_hours, event_name=event_name)

def confirm_reset():
    return True

def clear_files():
    with open('data/rawHours/attendance.txt', 'w') as f:
        f.truncate(0)

    with open('data/totalHours/hourTotals.txt', 'w') as f:
        f.truncate(0)
    
    if os.path.exists('data/totalHours/hourTotals.csv'):
        os.remove('data/totalHours/hourTotals.csv')

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

        student_totals = {student_id: 0 for student_id in student_ids}

        with open('data/rawHours/archive.txt', 'r') as f:
            lines = f.readlines()

        for line in lines:
            match = re.match(r'(\d+)\sChecked In at (.+?) and Checked Out at (.+?), Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
            if match:
                student_id, check_in_str, check_out_str, hours_str, minutes_str = match.groups()
                check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d %H:%M:%S.%f")
                check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d %H:%M:%S.%f")
                hours = int(hours_str)
                minutes = int(minutes_str)

                if student_id in student_ids and start_date <= check_in.date() <= end_date:
                    student_totals[student_id] += hours * 60 + minutes

        for student_id in student_totals:
            total_hours = student_totals[student_id] // 60
            student_totals[student_id] = {'hours': total_hours, 'met_reqs': total_hours >= hour_total}

        csv_filename = 'data/hourReports/hour_report.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Student ID', 'Total Hours', 'Met Requirements']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for student_id, totals in student_totals.items():
                writer.writerow({'Student ID': student_id, 'Total Hours': totals['hours'], 'Met Requirements': totals['met_reqs']})

        return send_file(csv_filename, as_attachment=True)
    else:
        return render_template('hour_report.html', version=version_number, r_string = r_string)

def validate_student_id(student_id):
    global id_validation_enabled
    # Read ID validation state from file
    try:
        with open('data/id_validation_state.txt', 'r') as f:
            id_validation_enabled = f.read().strip().lower() == 'true'
    except FileNotFoundError:
        id_validation_enabled = False 

    if not id_validation_enabled and student_id.isdigit() and len(student_id) == 6:
        return True

    with open('data/valid_students.txt', 'r') as file:
        valid_ids = file.readlines()
    valid_ids = [line.strip().split(' | ')[0] for line in valid_ids]
    return student_id in valid_ids

@app.route('/valid_students_content', methods=['GET'])
def get_valid_students_content():
    with open('data/valid_students.txt', 'r') as file:
        content = file.read()
    return content

@app.route('/save_valid_students', methods=['POST'])
def save_valid_students():
    content = request.json.get('content')
    with open('data/valid_students.txt', 'w') as file:
        file.write(content)
    return {'message': 'Valid students list updated successfully.'}, 200

@app.route('/toggle_id_validation', methods=['POST'])
def toggle_id_validation():
    global id_validation_enabled
    id_validation_enabled = not id_validation_enabled

    with open('data/id_validation_state.txt', 'w') as f:
        f.write(str(id_validation_enabled)) # Write True/False as string
    
    return json.dumps({'id_validation_enabled': id_validation_enabled})

@app.route('/WestwoodRobotics/' + random_string + '/hour_corrector', methods=['GET', 'POST'])
def hours_corrector():
    message = ""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        date_of_correction = request.form.get('date_of_correction')
        hours_option = request.form.get('hours_option')
        file_selection = request.form.getlist('file_selection')

        result = attendance.correct_hours(student_id, date_of_correction, hours_option, file_selection)
        if isinstance(result, str): 
            message = result
        else:
            message = "Hours corrected successfully!"
    else:
        message = ""
    attendance_files = [filename for filename in os.listdir("data") if filename.startswith("attendance")]
    return render_template('hour_corrector.html', attendance_files=attendance_files, random_string=random_string, message = message)

@app.route('/check_exclusive_checkin/<student_id>/<date_of_correction>', methods=['POST'])
def check_exclusive_checkin(student_id, date_of_correction):
    exists = False
    selected_files = request.json.get('files', []) 
    for filename in selected_files: 
        file_path = os.path.join("data", filename)
        with open(file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith(f"{student_id} Checked In") and str(date_of_correction) in line and "Checked Out" not in line:
                    exists = True
                    break 
        if exists:
            break

@app.route('/volunteer-hours', methods=['GET', 'POST'])
def volunteer_hours():
    if request.method == 'POST':
        event = request.form.get('event')
        eventName = request.form.get('eventName')
        return redirect(url_for('event_hours', eventname=event))

    with open('data/event_list.txt', 'r') as file:
        events = file.readlines()

    return render_template('volunteer_hours.html', events=events, version=version_number)

    return json.dumps({'exists': exists})

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
    
@app.route('/hours', methods=['GET'])
def calculate_total_time():
    totals = {}
    suspicious_activity = []
    incomplete_entries = []
    complete_entries = []  # List to store complete entries

    # Read existing totals from hourTotals.txt
    if os.path.exists('data/totalHours/hourTotals.txt'):
        with open('data/totalHours/hourTotals.txt', 'r') as f:
            for line in f:
                match = re.match(r'ID: (\d+), Total time: (\d+) hours (\d+) minutes', line.strip())
                if match:
                    id, hours, minutes = match.groups()
                    totals[id] = {'hours': int(hours), 'minutes': int(minutes)}

    # Add new totals from attendance.txt
    if os.path.exists('data/rawHours/attendance.txt'):
        with open('data/rawHours/attendance.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                match = re.match(r'(\d+) Checked In at .+ and Checked Out at .+, Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
                if match:
                    id, hours, minutes = match.groups()
                    hours = int(hours)
                    minutes = int(minutes)
                    if hours >= 10:
                        suspicious_activity.append(line)
                    else:
                        if id not in totals:
                            totals[id] = {'hours': 0, 'minutes': 0}
                        totals[id]['hours'] += hours
                        totals[id]['minutes'] += minutes
                        complete_entries.append(line)  # Add complete entry to the list
                else:
                    incomplete_entries.append(line)

    # Convert minutes to hours
    for id in totals:
        hours, minutes = divmod(totals[id]['minutes'], 60)
        totals[id]['hours'] += hours
        totals[id]['minutes'] = minutes

    # Write to hourTotals.txt 
    with open('data/totalHours/hourTotals.txt', 'w') as f:
        for id, time in totals.items():
            f.write(f"ID: {id}, Total time: {time['hours']} hours {time['minutes']} minutes\n")

    # Append complete entries to archive.txt
    with open('data/rawHours/archive.txt', 'a') as archive:
        for entry in complete_entries:
            archive.write(entry + '\n')

    # Sort archive.txt
    with open('data/rawHours/archive.txt', 'r') as archive:
        lines = archive.readlines()
        sorted_lines = quicksort(lines)
    with open('data/rawHours/archive.txt', 'w') as archive:
        archive.writelines(sorted_lines)

    # Clear attendance.txt
    open('data/rawHours/attendance.txt', 'w').close()

    # Write incomplete entries to attendance.txt
    with open('data/rawHours/attendance.txt', 'w') as f:
        for line in incomplete_entries:
            f.write(line + '\n')

    # Write suspicious activity to file
    with open('data/suspicious_activity.txt', 'w') as f:
        for line in suspicious_activity:
            f.write(line + '\n')

    with open('data/totalHours/hourTotals.txt', 'r') as f:
        data = f.read()
    return render_template('hours.html', data=data, version=version_number)



def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()