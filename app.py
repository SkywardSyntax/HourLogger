1 import subprocess
2 from flask import Flask, request, redirect, session, url_for, render_template
3 from flask import Flask, request, redirect, url_for, render_template, Response
4 from flask import send_file
5 from HoursAdder import calculate_total_time  
6 import datetime
7 import re
8 import random
9 import string
10 import threading
11 import os
12 from flask import send_from_directory
13 import sys
14 import time
15 
16 app = Flask(__name__)
17 app.secret_key = 'skywardsyntazx'
18 random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
19 r_string = ("/" + random_string)
20 python_executable = sys.executable
21 
22 # Implement a global dictionary to track the last request time for each client IP address.
23 client_cooldowns = {}
24 client_request_counts = {}
25 
26 # Read version number from version.txt
27 with open('version.txt', 'r') as version_file:
28     version_number = version_file.read().strip()
29 
30 class Attendance:
31     def __init__(self):
32         # Read the data from attendanceBackup.txt
33         with open('attendanceBackup.txt', 'r') as backup_file:
34             backup_data = backup_file.read()
35 
36         # Write the backup data to attendance.txt
37         with open('attendance.txt', 'w') as attendance_file:
38             attendance_file.write(backup_data)
39         
40         self.records = {}
41     def check_in(self, id):
42         print(f"check_in called with id {id}")
43 
44 
45         now = datetime.datetime.now()
46         if id not in self.records or 'check_out_time' in self.records[id]:
47             self.records[id] = {'check_in_time': now}
48             if not os.path.exists('attendance.txt'):
49                 print("attendance.txt does not exist")
50                 open('attendance.txt', 'w').close()
51             with open('attendance.txt', 'a') as f:
52                 f.write(f"{id} Checked In at {now}\n")
53             subprocess.run([python_executable, 'attendanceBackup.py'])
54             return "Checked In!"
55     
56         
57         
58         else:
59             return "Already Checked In!"
60 
61     def check_in_event(self, id, event):
62         print(f"check_in-event called with id {id} and event {event}")
63 
64         now = datetime.datetime.now()
65         attendance_file = os.path.join(os.getcwd(), f'attendance-{event}.txt')
66         print(f"attendance file: {attendance_file}")
67         with open(attendance_file, 'a') as f:
68             print("attendance_file: " + attendance_file + " opened")
69             f.write(f"{id} Checked In at {now}\n")  # Use f-string for string formatting
70 
71         # Read the file's contents
72         with open(attendance_file, 'r') as f:
73             contents = f.read()
74         print(f"Contents of {attendance_file}:\n{contents}")
75 
76         return "Checked In - Event!"
77 
78 
79 
80     def check_out(self, id):
81         print(f"check_out called with id {id}")
82 
83         now = datetime.datetime.now()
84         check_in_time = None
85         if not os.path.exists('attendance.txt'):
86             print("attendance.txt does not exist")
87             open('attendance.txt', 'w').close()
88         # Check if the user has an incomplete entry in the attendance.txt file
89         with open('attendance.txt', 'r') as f:
90             lines = f.readlines()
91         # Check if the user has an incomplete entry in the attendance.txt file
92         with open('attendance.txt', 'r') as f:
93             lines = f.readlines()
94 
95         for i, line in enumerate(lines):
96             if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
97                 check_in_time_str = line.split(" at ")[1].strip()
98                 check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
99                 break
100 
101         if check_in_time is not None or (id in self.records and 'check_in_time' in self.records[id]):
102             if check_in_time is None:
103                 check_in_time = self.records[id]['check_in_time']
104             time_diff = now - check_in_time
105 
106             # Convert time_diff from seconds to minutes and hours
107             total_seconds = time_diff.total_seconds()
108             hours, remainder = divmod(total_seconds, 3600)
109             minutes, _ = divmod(remainder, 60)
110 
111             self.records[id] = {'check_out_time': now}
112 
113             # Update the relevant line
114             for i, line in reversed(list(enumerate(lines))):
115                 if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
116                     lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
117                     break
118 
119             # Write the updated content back to the file
120             with open('attendance.txt', 'w') as f:
121                 print("attendance.txt exists")
122                 f.writelines(lines)
123 
124             subprocess.run([python_executable, 'attendanceBackup.py'])            
125             return f"Checked Out! Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes"
126         else:
127             return "Not Checked In!"
128         
129     def check_out_event(self, id, event):
130         print(f"check_out called with id {id}")
131 
132         now = datetime.datetime.now()
133         check_in_time = None
134         attendance_file = f'attendance-{event}.txt'
135         if not os.path.exists(attendance_file):
136             print(f"{attendance_file} does not exist")
137             open(attendance_file, 'w').close()
138         with open(attendance_file, 'r') as f:
139             lines = f.readlines()
140 
141         for i, line in enumerate(lines):
142             if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
143                 check_in_time_str = line.split(" at ")[1].strip()
144                 check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
145                 break
146 
147         if check_in_time is not None or (id in self.records and 'check_in_time' in self.records[id]):
148             if check_in_time is None:
149                 check_in_time = self.records[id]['check_in_time']
150             time_diff = now - check_in_time
151 
152             # Convert time_diff from seconds to minutes and hours
153             total_seconds = time_diff.total_seconds()
154             hours, remainder = divmod(total_seconds, 3600)
155             minutes, _ = divmod(remainder, 60)
156 
157             self.records[id] = {'check_out_time': now}
158 
159             # Update the relevant line
160             for i, line in reversed(list(enumerate(lines))):
161                 if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
162                     lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
163                     break
164 
165             # Write the updated content back to the file
166             with open(attendance_file, 'w') as f:
167                 print("attendance.txt exists")
168                 f.writelines(lines)
169         
170             return f"Checked Out! Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes"
171         else:
172             return "Not Checked In!"
173 
174     def check_status_and_act(self, id):
175         now = datetime.datetime.now()
176         print(f"check_status_and_act called with id {id}")
177 
178         # Check if the user has an incomplete entry in the attendance.txt file
179         with open('attendance.txt', 'r') as f:
180             lines = f.readlines()
181         for i, line in enumerate(lines):
182             if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
183                 check_in_time_str = line.split(" at ")[1].strip()
184                 check_in_time = datetime.datetime.strptime(check_in_time_str, "%Y-%m-%d %H:%M:%S.%f")
185                 time_diff = now - check_in_time
186 
187                 # Convert time_diff from seconds to minutes and hours
188                 total_seconds = time_diff.total_seconds()
189                 hours, remainder = divmod(total_seconds, 3600)
190                 minutes, _ = divmod(remainder, 60)
191 
192                 if hours >= 10:
193                     # If it's been more than 10 hours, check them out and check them in again
194                     lines[i] = f"{id} Checked In at {check_in_time} and Checked Out at {now}, Meeting Time Recorded: {int(hours)} hours {int(minutes)} minutes\n"
195                     with open('attendance.txt', 'w') as f:
196                         f.writelines(lines)
197                     return self.check_in(id)
198                 else:
199                     return self.check_out(id)
200 
201         # If the user doesn't have an incomplete entry, proceed as before
202         if id in self.records and 'check_in_time' in self.records[id] and 'check_out_time' not in self.records[id]:
203             return self.check_out(id)
204         else:
205             return self.check_in(id) if re.match(r'^\d{6}$', id) else "Invalid Student Id Number. Please enter only the 6 digit number."
206 
207 attendance = Attendance()  # Create an instance of Attendance
208 
209 def check_client_cooldown(client_ip):
210     current_time = time.time()
211     if client_ip not in client_request_counts:
212         client_request_counts[client_ip] = [current_time]
213     else:
214         client_request_counts[client_ip].append(current_time)
215         client_request_counts[client_ip] = [t for t in client_request_counts[client_ip] if current_time - t <= 1]
216         if len(client_request_counts[client_ip]) > 3:
217             if client_ip not in client_cooldowns or current_time - client_cooldowns[client_ip] >= 10:
218                 client_cooldowns[client_ip] = current_time
219                 return True
220     return False
221 
222 @app.route('/raw_hours', methods=['GET'])
223 def attendance_data():
224     client_ip = request.remote_addr
225     if check_client_cooldown(client_ip):
226         return redirect(url_for('cooldown'))
227     with open('attendance.txt', 'r') as f:
228         data = f.read()
229     return Response(data, mimetype='text/plain')
230 
231 
232 @app.route('/total_hours', methods=['GET'])
233 def total_data():
234     client_ip = request.remote_addr
235     if check_client_cooldown(client_ip):
236         return redirect(url_for('cooldown'))
237     with open('hourTotals.txt', 'r') as f:
238         data = f.read()
239     return Response(data, mimetype='text/plain')
240 
241 @app.route('/download_csv', methods=['GET'])
242 def download_file():
243     client_ip = request.remote_addr
244     if check_client_cooldown(client_ip):
245         return redirect(url_for('cooldown'))
246     subprocess.run([python_executable, 'sheetExporter.py'])
247     return send_file('hourTotals.csv', as_attachment=True)
248 
249 @app.route('/', methods=['GET', 'POST'])
250 def login():
251     error = None
252     if request.method == 'POST':
253         if request.form['username'] != 'admin' or request.form['password'] != 'secret':
254             error = 'Invalid Credentials. Please try again.'
255         else:
256             session['username'] = request.form['username']
257             return redirect('/' + random_string)
258     return render_template('login.html', error=error, version=version_number)
259 
260 @app.route('/volunteer+HASHSTRING', methods=['GET'])
261 def handle_volunteer():
262     return redirect("/volunteer" + r_string)
263 
264 @app.route('/' + random_string, methods=['GET', 'POST'])
265 def home():
266     client_ip = request.remote_addr
267     if check_client_cooldown(client_ip):
268         return redirect(url_for('cooldown'))
269     message = ''
270     if request.method == 'POST':
271         id = request.form.get('id')
272         message = attendance.check_status_and_act(id)
273     return render_template('home.html', message=message, version=version_number)
274 
275 
276 @app.route('/WestwoodRoboticsAdmin', methods=['GET'])
277 def admin():
278     if 'username' in session and session['username'] == 'admin':
279         return render_template('admin.html', version=version_number)
280     else:
281         session['next_url'] = url_for('admin')
282         return redirect(url_for('loginz'))
283 
284 @app.route('/login', methods=['GET', 'POST'])
285 def loginz():
286     if request.method == 'POST':
287         username = request.form.get('username')
288         password = request.form.get('password')
289         if username == 'admin' and password == 'secret':  # change 'password' to 'secret'
290             session['username'] = username
291             next_url = session.pop('next_url', url_for('home'))
292             return redirect(next_url)
293         else:
294             return "Invalid username or password", 401
295     return render_template('login.html', version=version_number)
296 
297 
298     
299 @app.route('/logout', methods=['GET'])
300 def logout():
301     session.pop('username', None)
302     return redirect(url_for('login'))
303 
304 # Add this new route to your Flask application
305 @app.route('/calculate_hours', methods=['GET'])
306 def calculate_hours():
307     client_ip = request.remote_addr
308     if check_client_cooldown(client_ip):
309         return redirect(url_for('cooldown'))
310     subprocess.run([python_executable, 'HoursAdder.py'])
311     return redirect(url_for('admin'))
312 
313 @app.route('/archive', methods=['GET'])
314 def archives():
315     # Get the list of .txt files in the Archives folder
316     archive_files = [file for file in os.listdir('Archives') if file.endswith('.txt')]
317     if 'username' in session and session['username'] == 'admin':
318         return render_template('archive.html', archive_files=archive_files, version=version_number)
319     else:
320         session['next_url'] = url_for('admin')
321         return redirect(url_for('loginz'))
322 
323 
324 
325 @app.route('/download/<filename>', methods=['GET'])
326 def download_archive(filename):
327     # Construct the full file path by joining the 'Archives' folder and the selected filename
328     file_path = os.path.join('Archives', filename)
329 
330     # Check if the file exists
331     if not os.path.exists(file_path):
332         return "File not found"
333 
334     # Return the file as an attachment
335     return send_from_directory('Archives', filename, as_attachment=True)
336 
337 
338 @app.route('/reset_all', methods=['GET'])
339 def reset_all():
340     if confirm_reset():
341         clear_files()
342         return redirect(url_for('admin'))
343     else:
344         return "Reset action canceled."
345 
346 @app.route('/hours', methods=['GET'])
347 def hours():
348     client_ip = request.remote_addr
349     if check_client_cooldown(client_ip):
350         return redirect(url_for('cooldown'))
351     subprocess.run([python_executable, 'HoursAdder.py'])
352     with open('hourTotals.txt', 'r') as f:
353         data = f.read()
354     return render_template('hours.html', data=data, version=version_number)
355 
356 @app.route('/volunteer' + r_string, methods=['GET', 'POST'])
357 def volunteer():
358     error = None
359     if request.method == 'POST':
360         username = request.form.get('username')  # Added to handle username input
361         password = request.form.get('password')
362         if username != 'admin' or password != 'secret':  # Modified to check both username and password
363             error = "Incorrect Credentials"
364             return render_template('volunteer.html', error=error, version=version_number)  # Modify to use render_template with error message
365         else:
366             return redirect('/volunteer-select' + r_string)
367     return render_template('volunteer.html', error=error, version=version_number)  # Modify to include error handling
368 
369 @app.route('/volunteer-select' + r_string, methods=['GET', 'POST'])
370 def volunteer_select():
371     if request.method == 'POST':
372         event = request.form.get('event')
373         # Create a new file for each event
374         with open(f'attendance-{event}.txt', 'w') as f:
375             pass
376         return redirect(url_for('volunteer_login', event=event))
377     return render_template('volunteer_select.html', version=version_number)  # Create a new HTML template for this page
378 
379 @app.route('/volunteer-login' + r_string, methods=['GET', 'POST'])
380 def volunteer_login():
381     message = ''
382     event = request.args.get('event')
383     if request.method == 'POST':
384         id = request.form.get('id')
385         # Check credentials and provide an error message if incorrect
386         if id != 'expected_id':  # This is a placeholder condition
387             error = "Incorrect ID. Please try again."
388             return render_template('volunteer_login.html', error=error, event=event, version=version_number)
389         # Proceed with the rest of the function if credentials are correct
390         event = request.args.get('event')  # Get the event value from the query string parameter
391         print("volunteer login" + event + " id:" + id)
392         # Use the event-specific attendance file
393         attendance_file = f'attendance-{event}.txt'
394 
395         # Check if the user has an incomplete entry in the attendance file
396         with open(attendance_file, 'r') as f:
397             lines = f.readlines()
398         for i, line in enumerate(lines):
399             if line.startswith(f"{id} Checked In") and "Checked Out" not in line:
400                 # If the user has an incomplete entry, check them out
401                 message = attendance.check_out_event(id, event)
402                 break
403         else:
404             # If the user doesn't have an incomplete entry, check them in
405             message = attendance.check_in_event(id, event)
406 
407     return render_template('volunteer_login.html', message=message, event=event, version=version_number)  # Modify to include event name in the template
408 
409 @app.route('/<eventname>-hours' + r_string, methods=['GET'])
410 def event_hours(eventname):
411     event_file = f'attendance-{eventname}.txt'
412     event_totals_file = f'{eventname}-HourTotals.txt'
413     volunteer_totals_file = 'VolunteerHourTotals.txt'
414 
415     # Initialize a dictionary to store the total hours for each volunteer
416     event_totals = {}
417     volunteer_totals = {}
418 
419     # Read the event-specific attendance file
420     with open(event_file, 'r') as f:
421         lines = f.readlines()
422         for line in lines:
423             match = re.match(r'(\d+)\sChecked In at (.+?) and Checked Out at (.+?), Meeting Time Recorded: (\d+) hours (\d+) minutes', line)
424             if match:
425                 id, check_in_time_str, check_out_time_str, hours_str, minutes_str = match.groups()
426 
427             hours = int(hours_str) if hours_str.isdigit() else 0
428             minutes = int(minutes_str) if minutes_str.isdigit() else 0
429             total_minutes = hours * 60 + minutes
430 
431             # Add the total minutes to the event_totals dictionary
432             if id in event_totals:
433                 event_totals[id] += total_minutes
434             else:
435                 event_totals[id] = total_minutes
436 
437     # Write the event_totals to the event_totals_file
438     with open(event_totals_file, 'w') as f:
439         for id, total_minutes in event_totals.items():
440             hours, minutes = divmod(total_minutes, 60)
441             f.write(f"{id} Total Time: {hours} hours {minutes} minutes\n")
442 
443     # If the volunteer_totals_file exists, read it and update the volunteer_totals dictionary
444     if os.path.exists(volunteer_totals_file):
445         with open(volunteer_totals_file, 'r') as f:
446             lines = f.readlines()
447             for line in lines:
448                 id, _, _, rest = line.split(None, 3)
449                 hours_str, _, minutes_str = rest.rsplit(None, 2)
450                 hours = int(hours_str) if hours_str.isdigit() else 0
451                 minutes = int(minutes_str) if minutes_str.isdigit() else 0
452                 total_minutes = hours * 60 + minutes
453 
454                 # Add the total minutes to the volunteer_totals dictionary
455                 if id in volunteer_totals:
456                     volunteer_totals[id] += total_minutes
457                 else:
458                     volunteer_totals[id] = total_minutes
459 
460     # Update the volunteer_totals dictionary with the event_totals
461     for id, total_minutes in event_totals.items():
462         if id in volunteer_totals:
463             volunteer_totals[id] += total_minutes
464         else:
465             volunteer_totals[id] = total_minutes
466 
467     # Write the updated volunteer_totals to the volunteer_totals_file
468     with open(volunteer_totals_file, 'w') as f:
469         for id, total_minutes in volunteer_totals.items():
470             hours, minutes = divmod(total_minutes, 60)
471             f.write(f"{id} Total Time: {hours} hours {minutes} minutes\n")
472     
473     with open(event_totals_file, 'r') as f:
474         data = f.read()
475 
476     return render_template('event_hours.html', data=data, eventname=eventname, version=version_number)  # Modify to include event name in the template
477 
478 def confirm_reset():
479     # Implement your logic to confirm the reset action here
480     # For example, you can check if the admin is logged in or prompt for a password
481     # Return True if the reset action is confirmed, False otherwise
482     return True
483 
484 def clear_files():
485     # Clear the contents of attendance.txt
486     with open('attendance.txt', 'w') as f:
487         f.truncate(0)
488 
489     # Clear the contents of hourTotals.txt
490     with open('hourTotals.txt', 'w') as f:
491         f.truncate(0)
492 
493     with open ('attendanceBackup.txt', 'w') as f:
494         f.truncate(0)
495     # Delete the hourTotals.csv file
496     if os.path.exists('hourTotals.csv'):
497         os.remove('hourTotals.csv')
498 
499 @app.route('/cooldown', methods=['GET'])
500 def cooldown():
501     return render_template('cooldown.html', version=version_number)
502 
503 def main():
504     app.run(debug=True)
505 
506 if __name__ == "__main__":
507     main()
508 
