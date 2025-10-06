import requests
import ssl
import socket
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- CONFIGURATION ----------------
URLS = [
    "https://www.amazon.com",
    "https://www.geeksforgeeks.org",
    "https://www.javatpoint.com",
    "https://www.flipkart.com"
]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "harshitkukreti22@gmail.com"
EMAIL_PASS = "harshit21011856@22"
EMAIL_TO = ["harhsitkukreti22@gmail.com", "autotest@gmail.com"]

# ---------------- HELPER FUNCTIONS ----------------
def check_availability(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200, response.elapsed.total_seconds(), None
    except Exception as e:
        return False, None, str(e)

def check_ssl_expiry(url):
    try:
        hostname = url.split("//")[-1].split("/")[0]
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry_date - datetime.utcnow()).days
                return days_left > 0, days_left, None
    except Exception as e:
        return False, None, str(e)

# ---------------- PRINT TABLES ----------------
def print_separate_tables(results):
    green_rows = []
    red_rows = []
    exception_rows = []

    for r in results:
        url = r["URL"]

        # Availability
        if r["Availability_Exception"]:
            exception_rows.append((url, "Availability", r["Availability_Exception"]))
        elif r["Availability"]:
            green_rows.append((url, "Availability"))
        else:
            red_rows.append((url, "Availability"))

        # Response
        if r["Response_Exception"]:
            exception_rows.append((url, "Response Time", r["Response_Exception"]))
        elif r["Response_OK"]:
            green_rows.append((url, "Response Time"))
        else:
            red_rows.append((url, "Response Time"))

        # SSL
        if r["SSL_Exception"]:
            exception_rows.append((url, "SSL", r["SSL_Exception"]))
        elif r["SSL_OK"]:
            green_rows.append((url, "SSL"))
        else:
            red_rows.append((url, "SSL"))

    # GREEN Table
    print("\n================== GREEN TABLE ==================")
    print(f"{'URL':<40} | {'Condition':<15}")
    print("-"*60)
    for url, condition in green_rows:
        print(f"{url:<40} | {condition:<15}")

    # RED Table
    print("\n================== RED TABLE ====================")
    print(f"{'URL':<40} | {'Condition':<15}")
    print("-"*60)
    for url, condition in red_rows:
        print(f"{url:<40} | {condition:<15}")

    # EXCEPTION Table
    print("\n================== EXCEPTION TABLE ==============")
    print(f"{'URL':<40} | {'Condition':<15} | {'Error':<30}")
    print("-"*90)
    for url, condition, error in exception_rows:
        print(f"{url:<40} | {condition:<15} | {error:<30}")

# ---------------- EMAIL FUNCTION (kept but not used) ----------------
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(EMAIL_TO)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    # Not sending email now to avoid Gmail issues
    print("\n[INFO] Email sending skipped in current mode.")

# ---------------- MAIN LOGIC ----------------
def main():
    results = []

    for url in URLS:
        avail, response_time, avail_exc = check_availability(url)
        response_ok = response_time is not None and response_time < 5
        response_exc = None if avail_exc is None else avail_exc

        ssl_ok, ssl_days, ssl_exc = check_ssl_expiry(url)

        results.append({
            "URL": url,
            "Availability": avail,
            "Availability_Exception": avail_exc,
            "Response_OK": response_ok,
            "Response_Exception": response_exc,
            "SSL_OK": ssl_ok,
            "SSL_Exception": ssl_exc
        })

    # Print tables
    print_separate_tables(results)

if __name__ == "__main__":
    main()
