# HourLogger

HourLogger is a Python-based project designed to log and manage the hours spent by individuals, identified by their IDs. The project consists of several Python scripts that perform different tasks.

## Scripts

1. `HoursRunner.py`: This script is responsible for the check-in and check-out process. It records the time when an individual checks in and checks out. The total time spent is calculated and stored in a file named `attendance.txt`.

2. `HoursAdder.py`: This script reads the `attendance.txt` file, calculates the total time spent by each individual, and stores the results in a file named `hourTotals.txt`. It also clears the `attendance.txt` file after the calculations.

3. `HoursWeb.py`: This script provides a web interface for the check-in and check-out process. It uses the Flask framework to create a web server. The check-in and check-out process is similar to the one in `HoursRunner.py`, but it's done through a web interface.

4. `sheetExporter.py`: This script reads the `hourTotals.txt` file and exports the data into a CSV file named `hourTotals.csv`. The CSV file contains the ID of each individual and their total time spent.

## Usage

To use the project, run the scripts in the following order:

1. Run `HoursRunner.py` or `HoursWeb.py` to check-in and check-out individuals.
2. Run `HoursAdder.py` to calculate the total time spent by each individual.
3. Run `sheetExporter.py` to export the data to a CSV file.

## Requirements

- Python 3.6 or higher
- Flask
