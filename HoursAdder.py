import re
import os
import shutil
import datetime

def calculate_total_time():
    totals = {}
    suspicious_activity = []
    # Read existing totals from hourTotals.txt
    if os.path.exists('hourTotals.txt'):
        with open('hourTotals.txt', 'r') as f:
            for line in f:
                match = re.match(r'ID: (\d+), Total time: (\d+) hours (\d+) minutes', line.strip())
                if match:
                    id, hours, minutes = match.groups()
                    totals[id] = {'hours': int(hours), 'minutes': int(minutes)}

    # Add new totals from attendance.txt
    with open('attendance.txt', 'r') as f:
        for line in f:
            line = line.strip()  # Strip newline character
            match = re.match(r'(\d+) Checked In at .+ and Checked Out at .+, Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
            if match:
                id, hours, minutes = match.groups()
                hours = int(hours)
                minutes = int(minutes)
                if hours >= 10:
                    suspicious_activity.append(line)
                    continue
                if id not in totals:
                    totals[id] = {'hours': 0, 'minutes': 0}
                totals[id]['hours'] += hours
                totals[id]['minutes'] += minutes

    # Convert minutes to hours
    for id in totals:
        hours, minutes = divmod(totals[id]['minutes'], 60)
        totals[id]['hours'] += hours
        totals[id]['minutes'] = minutes

    # Archive attendance.txt
    if not os.path.exists('Archives'):
        os.makedirs('Archives')
    today = datetime.date.today()
    shutil.copy('attendance.txt', f'Archives/Archive {today.month}-{today.day}-{today.year}.txt')

    # Clear attendance.txt
    open('attendance.txt', 'w').close()

    # Write suspicious activity to file
    with open('suspicious_activity.txt', 'w') as f:
        for line in suspicious_activity:
            f.write(line + '\n')

    return totals

totals = calculate_total_time()

with open('hourTotals.txt', 'w') as f:
    for id, time in totals.items():
        f.write(f"ID: {id}, Total time: {time['hours']} hours {time['minutes']} minutes\n")