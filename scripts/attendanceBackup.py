import os
import shutil
import time

def backup_attendance():
    # Initial copy from attendance.txt to attendanceBackup.txt
    shutil.copyfile("/workspaces/HourLogger/data/attendance.txt", "/workspaces/HourLogger/data/attendanceBackup.txt")

backup_attendance()
