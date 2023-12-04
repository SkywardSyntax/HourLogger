from flask import Flask, request, redirect, url_for, render_template
from flask import Flask, request, redirect, url_for, render_template, Response
import datetime
import re
import random
import string
import os

app = Flask(__name__)
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
r_string = ("/" + random_string)

class Attendance:
    def __init__(self):
        self.records = {}

    def check_in(self, id):
        now = datetime.datetime.now()
        if id not in self.records or 'check_out_time' in self.records[id]:
            self.records[id] = {'check_in_time': now}
            if not os.path.exists('attendance.txt'):
                open('attendance.txt', 'w').close()
            with open('attendance.txt', 'a') as f:
                f.write(f"{id} Checked In at {now}\n")
            return "Checked In!"
        else:
            return "Already Checked In!"
    def check_out(self, id):
        now = datetime.datetime.now()
        check_in_time = None
        if not os.path.exists('attendance.txt'):
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
                f.writelines(lines)
            return f"Checked Out! Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes"
        else:
            return "Not Checked In!"

    def check_status_and_act(self, id):
        now = datetime.datetime.now()

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

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'secret':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/' + random_string)
    return render_template('login.html', error=error)

@app.route('/' + random_string, methods=['GET', 'POST'])
def home():
    message = ''
    if request.method == 'POST':
        id = request.form.get('id')
        message = attendance.check_status_and_act(id)
    return render_template('home.html', message=message)


def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()


