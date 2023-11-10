from flask import Flask, request, redirect, url_for, render_template
import datetime
import re

app = Flask(__name__)

class Attendance:
    def __init__(self):
        self.records = {}
        self.line_numbers = {}

    def check_in(self, id):
        now = datetime.datetime.now()
        if id not in self.records or 'check_in_time' not in self.records[id]:
            self.records[id] = {'total_time': datetime.timedelta(), 'check_in_time': now}
            with open('attendance.txt', 'a') as f:
                f.write(f"{id}\n")
            with open('attendance.txt', 'r') as f:
                lines = f.readlines()
            self.line_numbers[id] = len(lines) - 1
            return "Checked In!"
        else:
            return "Already Checked In!"


    def check_out(self, id):
        now = datetime.datetime.now()
        if id in self.records and 'check_in_time' in self.records[id]:
            check_in_time = self.records[id]['check_in_time']
            time_diff = now - check_in_time
            self.records[id]['total_time'] += time_diff
            del self.records[id]['check_in_time']

            # Convert total_time from seconds to minutes and hours
            total_seconds = self.records[id]['total_time'].total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            # Read the file and update the relevant line
            with open('attendance.txt', 'r') as f:
                lines = f.readlines()
            lines[self.line_numbers[id]] = f"{id} {int(hours)} hours {int(minutes)} minutes\n"
            # Write the updated content back to the file
            with open('attendance.txt', 'w') as f:
                f.writelines(lines)
            return f"Checked Out! \nMeeting Time Recorded: {int(hours)} hours {int(minutes)} minutes"



    def get_total_time(self, id):
        if id in self.records:
            return self.records[id]['total_time']
        else:
            return None

    def check_status_and_act(self, id):
        if id in self.records and 'check_in_time' in self.records[id]:
            return self.check_out(id)
        else:
            return self.check_in(id) if re.match(r'^\d{6}$', id) else "Invalid Student Id Number. Please enter only the 6 digit number."



attendance = Attendance()  # Create an instance of Attendance

@app.route('/', methods=['GET', 'POST'])
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


