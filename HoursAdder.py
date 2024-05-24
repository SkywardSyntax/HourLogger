import csv
import re
import os
import datetime
import math

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

def calculate_total_time():
    totals = {}
    suspicious_activity = []
    incomplete_entries = []

    # Read existing totals from hourTotals.txt
    if not os.path.exists('hourTotals.txt'):
        open('hourTotals.txt', 'w').close()
    else:
        with open('hourTotals.txt', 'r') as f:
            for line in f:
                match = re.match(r'ID: (\d+), Total time: (\d+) hours (\d+) minutes', line.strip())
                if match:
                    id, hours, minutes = match.groups()
                    totals[id] = {'hours': int(hours), 'minutes': int(minutes)}

    # Add new totals from attendance.txt
    if not os.path.exists('attendance.txt'):
        open('attendance.txt', 'w').close()
    else:
        with open('attendance.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
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
                else:
                    # If the line does not match the pattern, it's an incomplete entry
                    incomplete_entries.append(line)

    # Convert minutes to hours
    for id in totals:
        hours, minutes = divmod(totals[id]['minutes'], 60)
        totals[id]['hours'] += hours
        totals[id]['minutes'] = minutes

    # Append attendance.txt to archive.txt
    with open('attendance.txt', 'r') as attendance, open('archive.txt', 'a') as archive:
        archive.writelines(attendance.readlines())

    # Sort archive.txt
    with open('archive.txt', 'r') as archive:
        lines = archive.readlines()
        sorted_lines = quicksort(lines)
    with open('archive.txt', 'w') as archive:
        archive.writelines(sorted_lines)

    # Clear attendance.txt
    open('attendance.txt', 'w').close()

    # Write incomplete entries to attendance.txt and attendanceBackup.txt
    with open('attendance.txt', 'w') as f:
        for line in incomplete_entries:
            f.write(line + '\n')
    with open('attendanceBackup.txt', 'w') as f:
        for line in incomplete_entries:
            f.write(line + '\n')

    # Write suspicious activity to file
    with open('suspicious_activity.txt', 'w') as f:
        for line in suspicious_activity:
            f.write(line + '\n')

    return totals

totals = calculate_total_time()

# Write totals to hourTotals.txt
with open('hourTotals.txt', 'w') as f:
    for id, time in totals.items():
        f.write(f"ID: {id}, Total time: {time['hours']} hours {time['minutes']} minutes\n")

totals = {}

# Read existing totals from hourTotals.txt
if not os.path.exists('hourTotals.txt'):
    open('hourTotals.txt', 'w').close()
else:
    with open('hourTotals.txt', 'r') as f:
        for line in f:
            match = re.match(r'ID: (\d+), Total time: (\d+) hours (\d+) minutes', line.strip())
            if match:
                id, hours, minutes = match.groups()
                totals[id] = {'hours': int(hours), 'minutes': int(minutes)}

# Write totals to hourTotals.csv
with open('hourTotals.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Total Hours'])  # Write the header
    for id, time in totals.items():
        total_hours = time['hours']
        total_minutes = time['minutes']

        # Round minutes to the nearest 15-minute interval
        remainder = total_minutes % 15
        if remainder >= 7.5:
            total_minutes += 15 - remainder
        else:
            total_minutes -= remainder

        # Convert total hours and minutes to a time string
        total_time = "{:02d}:{:02d}:{:02d}".format(total_hours, total_minutes, 0)

        writer.writerow([id, total_time])  # Write the data
