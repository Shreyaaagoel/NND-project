import re
import os
import json
import time
import platform
import threading
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv()

# Regex Patterns
CC_REGEX = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\+?\d{1,3}?[-. ]?\(?\d{1,4}\)?[-. ]?\d{1,4}[-. ]?\d{1,9}")

# Flag to determine encryption
encrypt_data = False

def toggle_encryption():
    global encrypt_data
    encrypt_data = not encrypt_data
    status = "🔒 ENABLED" if encrypt_data else "❌ DISABLED"
    encrypt_button.config(bg="green" if encrypt_data else "gray", text=status)
    encryption_status_label.config(text=f"Encryption: {status}")
    messagebox.showinfo("Encryption Status", f"Encryption {status}.")

def encrypt_sensitive_data(text):
    text = CC_REGEX.sub("****-****-****-****", text)
    text = EMAIL_REGEX.sub("[encrypted email]", text)
    text = PHONE_REGEX.sub("[encrypted phone]", text)
    return text

# Function to play an alert sound
def play_sound():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONHAND)
        elif platform.system() == "Darwin":  # macOS
            from playsound import playsound
            playsound("/System/Library/Sounds/Sosumi.aiff")
        else:  # Linux
            os.system("paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga")
    except Exception as e:
        print("Error playing sound:", e)

# Function to show alert safely in the GUI thread
def show_alert(alert_message):
    root.after(0, lambda: messagebox.showerror("Security Alert", alert_message))

# Function to check for sensitive data
def check_sensitive_data(input_text):
    if encrypt_data:
        encrypted_text = encrypt_sensitive_data(input_text)
        messagebox.showinfo("Encrypted Data", f"Sensitive data encrypted:\n{encrypted_text}")
        return  # Skip detection alerts when encryption is enabled
    
    alert_message = "⚠️ Sensitive data detected:\n"
    found = False

    if CC_REGEX.search(input_text):
        alert_message += "- Credit Card Detected\n"
        found = True
    if EMAIL_REGEX.search(input_text):
        alert_message += "- Email Address Detected\n"
        found = True
    if PHONE_REGEX.search(input_text):
        alert_message += "- Phone Number Detected\n"
        found = True

    if found:
        play_sound()
        show_alert(alert_message)  # Call GUI alert safely

# Function to manually check user input
def manual_check():
    user_input = text_entry.get("1.0", tk.END).strip()
    check_sensitive_data(user_input)

# Function to monitor network traffic in real-time using Chrome DevTools Protocol (CDP)
def start_network_monitoring():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in the background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_cdp_cmd("Network.enable", {})

    print("Monitoring network traffic...")

    try:
        while True:
            logs = driver.get_log("performance")
            for entry in logs:
                try:
                    log_data = json.loads(entry["message"])["message"]
                    if log_data["method"] == "Network.requestWillBeSent":
                        request = log_data["params"]["request"]
                        if request["method"] == "POST":
                            post_data = request.get("postData", "")
                            if encrypt_data:
                                post_data = encrypt_sensitive_data(post_data)
                            check_sensitive_data(post_data)  # Now triggers GUI alert!
                except Exception as e:
                    print("Error processing log entry:", e)
            time.sleep(1)  # Reduced delay for real-time monitoring
    except Exception as e:
        print(f"Monitoring stopped: {e}")
    finally:
        driver.quit()

# Function to run network monitoring in a separate thread
def run_network_monitoring():
    monitoring_thread = threading.Thread(target=start_network_monitoring, daemon=True)
    monitoring_thread.start()
    messagebox.showinfo("Network Monitor", "Real-time network monitoring started!")

# Create GUI
root = tk.Tk()
root.title("Sensitive Data Checker & Network Monitor")
root.geometry("550x600")  # Adjusted size for better UI

tk.Label(root, text="Enter text to check:", font=("Arial", 12)).pack(pady=10)
text_entry = tk.Text(root, height=5, width=50)
text_entry.pack()

tk.Button(root, text="Check for Sensitive Data", command=manual_check, bg="red", fg="white", font=("Arial", 12)).pack(pady=10)
encrypt_button = tk.Button(root, text="To Encrypt", command=toggle_encryption, bg="gray", fg="white", font=("Arial", 12))
encrypt_button.pack(pady=10)
encryption_status_label = tk.Label(root, text="Encryption: ❌ DISABLED", font=("Arial", 12))
encryption_status_label.pack()
tk.Button(root, text="Check Network Monitoring", command=run_network_monitoring, bg="blue", fg="white", font=("Arial", 12)).pack(pady=10)

root.mainloop()
