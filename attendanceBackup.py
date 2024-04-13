import os
import shutil
import time

def backup_attendance():
    # Initial copy from attendance.txt to attendanceBackup.txt
    shutil.copyfile("attendance.txt", "attendanceBackup.txt")

backup_attendance()