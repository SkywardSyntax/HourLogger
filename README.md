# HourLogger

HourLogger is a Python-based project designed to log and manage the hours spent by individuals, identified by their IDs. The project consists of several Python scripts that perform various tasks.

## Main Application

### `app.py`

The `app.py` file is the main application file that contains the core functionality of the project. It uses the Flask framework to create a web server and provides various routes for different functionalities.

#### Core Functionality

- **Attendance Management**: The `Attendance` class is responsible for managing the check-in and check-out process. It records the time when an individual checks in and checks out, calculates the total time spent, and stores the data in various files.
- **Event Management**: The application supports event-based attendance tracking. Each event has its own attendance file, and the total hours for each event are calculated separately.
- **Web Interface**: The application provides a web interface for the check-in and check-out process, as well as for administrative tasks.

#### Routes

- `/`: Home page for check-in and check-out.
- `/raw_hours`: View raw attendance data.
- `/total_hours`: View total hours data.
- `/download_csv`: Download the total hours data as a CSV file.
- `/admin`: Admin page for managing the application.
- `/calculate_hours`: Calculate the total hours for all individuals.
- `/archive`: View archived attendance files.
- `/download/<filename>`: Download a specific archived file.
- `/volunteer+HASHSTRING`: Redirect to the volunteer login page.
- `/<random_string>`: Home page for check-in and check-out with a random string in the URL.
- `/WestwoodRoboticsAdmin`: Admin login page.
- `/admin_login`: Admin login page.
- `/logout`: Logout from the admin session.
- `/hour_report`: Generate a report of hours for a specific date range.
- `/valid_students_content`: Get the content of the valid students list.
- `/save_valid_students`: Save the updated valid students list.
- `/toggle_id_validation`: Toggle the ID validation state.
- `/WestwoodRobotics/<random_string>/hour_corrector`: Correct hours for a specific student.
- `/check_exclusive_checkin/<student_id>/<date_of_correction>`: Check if a student has an exclusive check-in for a specific date.
- `/event-hours`: View hours for a specific event.
- `/volunteer-hours`: View total volunteer hours.
- `/hours`: Calculate and view total hours.
- `/correct_checkout`: Correct the check-out time for a specific student.

## Web Interface

The web interface is provided by the `app.py` file and uses various HTML templates for different pages.

### HTML Templates

- `templates/admin.html`: Admin page for managing the application.
- `templates/home.html`: Home page for check-in and check-out.
- `templates/admin_login.html`: Admin login page.
- `templates/archive.html`: View archived attendance files.
- `templates/cooldown.html`: Cooldown notice page.
- `templates/event_hours.html`: View hours for a specific event.
- `templates/event_no_exist.html`: Event not found page.
- `templates/hour_corrector.html`: Correct hours for a specific student.
- `templates/hour_report.html`: Generate a report of hours for a specific date range.
- `templates/hours.html`: View total hours.
- `templates/login.html`: Officer login page.
- `templates/raw_hours.html`: View raw attendance data.
- `templates/total_volunteer_hours.html`: View total volunteer hours.
- `templates/view_archive.html`: View a specific archived file.
- `templates/volunteer.html`: Volunteer login page.
- `templates/volunteer_hours.html`: View hours for a specific event.
- `templates/volunteer_login.html`: Volunteer login page.
- `templates/volunteer_select.html`: Select an event for volunteer login.
- `templates/volunteer_select_unlocked.html`: Select an unlocked event for volunteer login.

## GitHub Actions Workflow

The project includes a GitHub Actions workflow defined in `.github/workflows/main.yml`. This workflow is used for continuous integration and deployment.

### Workflow Steps

1. **Compile and Runtime Check**: The workflow sets up Python, installs dependencies, and runs the `app.py` file using Gunicorn to check for any runtime errors.
2. **Build**: The workflow removes the `__pycache__` directory, moves data files out of the repository to preserve them across deployments, pulls the latest code, and moves the data files back into the repository.
3. **Start Gunicorn Server**: The workflow stops any existing Gunicorn server and starts a new one in a screen session.

## Scripts

1. `HoursRunner.py`: This script is responsible for the check-in and check-out process. It records the time when an individual checks in and checks out. The total time spent is calculated and stored in a file named `attendance.txt`.

2. `HoursAdder.py`: This script reads the `attendance.txt` file, calculates the total time spent by each individual, and stores the results in a file named `hourTotals.txt`. It also clears the `attendance.txt` file after the calculations.

3. `HoursWeb.py`: This script provides a web interface for the check-in and check-out process. It uses the Flask framework to create a web server. The check-in and check-out process is similar to the one in `HoursRunner.py`, but it's done through a web interface.

4. `sheetExporter.py`: This script reads the `hourTotals.txt` file and exports the data into a CSV file named `hourTotals.csv`. The CSV file contains the ID of each individual and their total time spent.

## Data Files

The application uses various data files to store attendance and hour data.

- `data/rawHours/attendance.txt`: Stores the raw attendance data.
- `data/totalHours/hourTotals.txt`: Stores the total hours data.
- `data/totalHours/hourTotals.csv`: Stores the total hours data in CSV format.
- `data/eventRawHours/attendance-<event>.txt`: Stores the raw attendance data for a specific event.
- `data/eventTotalHours/<event>-HourTotals.txt`: Stores the total hours data for a specific event.
- `data/hourReports/hour_report.csv`: Stores the generated hour report.
- `data/id_validation_state.txt`: Stores the ID validation state.
- `data/login.txt`: Stores the login credentials for the admin.
- `data/valid_students.txt`: Stores the list of valid student IDs.
- `data/version.txt`: Stores the version number of the application.
- `data/event_list.txt`: Stores the list of events.
- `data/rawHours/archive.txt`: Stores the archived raw attendance data.
- `data/suspicious_activity.txt`: Stores the suspicious activity data.

## Usage

To use the project, follow these steps:

1. Run `app.py` to start the web server.
2. Use the web interface to check-in and check-out individuals.
3. Use the admin page to calculate the total hours, generate reports, and manage the application.
4. Use the GitHub Actions workflow for continuous integration and deployment.

## Requirements

- Python 3.6 or higher
- Flask
