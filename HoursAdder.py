def calculate_total_time():
    totals = {}
    with open('attendance.txt', 'r') as f:
        for line in f:
            line = line.strip()  # Strip newline character
            print(f"Reading line: {line}")  # Debugging print statement
            parts = line.split()
            if len(parts) == 5:  # id, hours, number, minutes, number
                id = parts[0]
                hours = int(parts[1])
                minutes = int(parts[3])
                if id not in totals:
                    totals[id] = {'hours': 0, 'minutes': 0}
                totals[id]['hours'] += hours
                totals[id]['minutes'] += minutes
                print(f"Updated totals: {totals}")  # Debugging print statement

    # Convert minutes to hours
    for id in totals:
        hours, minutes = divmod(totals[id]['minutes'], 60)
        totals[id]['hours'] += hours
        totals[id]['minutes'] = minutes

    return totals

totals = calculate_total_time()
print(f"Final totals: {totals}")  # Debugging print statement

with open('hourTotals.txt', 'w') as f:
    for id, time in totals.items():
        f.write(f"ID: {id}, Total time: {time['hours']} hours {time['minutes']} minutes\n")