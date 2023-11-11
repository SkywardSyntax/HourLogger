import re
import os

def calculate_total_time():
    totals = {}
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
            parts = line.split()
            if len(parts) == 5:  # id, hours, number, minutes, number
                id = parts[0]
                hours = int(parts[1])
                minutes = int(parts[3])
                if id not in totals:
                    totals[id] = {'hours': 0, 'minutes': 0}
                totals[id]['hours'] += hours
                totals[id]['minutes'] += minutes

    # Convert minutes to hours
    for id in totals:
        hours, minutes = divmod(totals[id]['minutes'], 60)
        totals[id]['hours'] += hours
        totals[id]['minutes'] = minutes

    # Clear attendance.txt
    open('attendance.txt', 'w').close()

    return totals

totals = calculate_total_time()

with open('hourTotals.txt', 'w') as f:
    for id, time in totals.items():
        f.write(f"ID: {id}, Total time: {time['hours']} hours {time['minutes']} minutes\n")