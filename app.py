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

app = Flask(__name__)
app.secret_key = 'skywardsyntazx'
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
r_string = ("/" + random_string)

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
            subprocess.run(['python', 'attendanceBackup.py'])
            return "Checked In!"
        
        
        else:
            return "Already Checked In!"


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
            for i, line in enumerate(lines):
                if line.startswith(f"{id} Checked In"):
                    lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
                    break

            # Write the updated content back to the file
            with open('attendance.txt', 'w') as f:
                print("attendance.txt exists")
                f.writelines(lines)

            subprocess.run(['python', 'attendanceBackup.py'])
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

@app.route('/raw_hours', methods=['GET'])
def attendance_data():
    with open('attendance.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')


@app.route('/total_hours', methods=['GET'])
def total_data():
    with open('hourTotals.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')

@app.route('/download_csv', methods=['GET'])
def download_file():
    subprocess.run(['python', 'sheetExporter.py'])
    return send_file('hourTotals.csv', as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'secret':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['username']
            return redirect('/' + random_string)
    return render_template('login.html', error=error)

@app.route('/' + random_string, methods=['GET', 'POST'])
def home():
    message = ''
    if request.method == 'POST':
        id = request.form.get('id')
        message = attendance.check_status_and_act(id)
    return render_template('home.html', message=message)


@app.route('/WestwoodRoboticsAdmin', methods=['GET'])
def admin():
    if 'username' in session and session['username'] == 'admin':
        return render_template('admin.html')
    else:
        session['next_url'] = url_for('admin')
        return redirect(url_for('loginz'))

@app.route('/login', methods=['GET', 'POST'])
def loginz():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'secret':  # change 'password' to 'secret'
            session['username'] = username
            next_url = session.pop('next_url', url_for('home'))
            return redirect(next_url)
        else:
            return "Invalid username or password", 401
    return render_template('login.html')


    
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Add this new route to your Flask application
@app.route('/calculate_hours', methods=['GET'])
def calculate_hours():
    subprocess.run(['python', 'HoursAdder.py'])
    return redirect(url_for('admin'))

@app.route('/archive', methods=['GET'])
def archives():
    # Get the list of .txt files in the Archives folder
    archive_files = [file for file in os.listdir('Archives') if file.endswith('.txt')]
    if 'username' in session and session['username'] == 'admin':
        return render_template('archive.html', archive_files=archive_files)
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


def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()


