import csv
import re


open('data/totalHours/hourTotals.csv', 'w').close()

with open('data/totalHours/hourTotals.txt', 'r') as f:
    lines = f.readlines()

data = []
for line in lines:
    match = re.match(r'ID: (\d+), Total time: (\d+) hours (\d+) minutes', line.strip())
    if match:
        id, hours, minutes = match.groups()
        data.append([id, f"{int(hours):02d}:{int(minutes):02d}:00"])

with open('data/totalHours/hourTotals.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Total Time'])
    writer.writerows(data)

