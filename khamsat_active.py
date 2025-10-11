import json
import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIES_FILE = "cookies.json"
TARGET_URL = "https://khamsat.com/"

CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,ar-AE;q=0.8,ar;q=0.7",
    "Upgrade-Insecure-Requests": "1",
    "Sec-CH-UA": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Referer": "https://accounts.hsoub.com/",
}


def send_email_notification(subject: str, body: str) -> None:
    """Send an email using SMTP settings from environment variables.

    Required env vars:
      - SMTP_HOST
      - SMTP_PORT (int)
      - SMTP_FROM
      - SMTP_TO (comma-separated for multiple)
    Optional env vars:
      - SMTP_USER, SMTP_PASSWORD (for auth)
      - SMTP_USE_TLS (default: true)
      - SMTP_USE_SSL (default: false). If true, SSL is used instead of starttls.
    """
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = os.getenv("SMTP_PORT", "465")
    sender = os.getenv("SMTP_FROM", "qozeemmonsurudeen@gmail.com'")
    recipients = os.getenv("SMTP_TO", 'qozeemmonsurudeen@gmail.com')
    user = os.getenv("SMTP_USER", "qozeemmonsurudeen@gmail.com")
    password = os.getenv("SMTP_PASSWORD","rzjf yqvo rvpl chuv")

    use_tls = (os.getenv("SMTP_USE_TLS", "false").lower() in ("1", "true", "yes", "y"))
    use_ssl = (os.getenv("SMTP_USE_SSL", "true").lower() in ("1", "true", "yes", "y"))

    if not host or not port or not sender or not recipients:
        print("✉️ Email not sent: missing SMTP env vars (SMTP_HOST, SMTP_PORT, SMTP_FROM, SMTP_TO)")
        return

    try:
        to_list = [addr.strip() for addr in recipients.split(",") if addr.strip()]
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.set_content(body)

        port_i = int(port)
        if use_ssl:
            with smtplib.SMTP_SSL(host, port_i) as smtp:
                if user and password:
                    smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port_i) as smtp:
                smtp.ehlo()
                if use_tls:
                    try:
                        smtp.starttls()
                    except Exception as e:
                        print(f"⚠️ STARTTLS failed: {e}")
                if user and password:
                    smtp.login(user, password)
                smtp.send_message(msg)
        print("✅ Notification email sent")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def setup_driver():
    chrome_options = Options()
    # chrome_options.binary_location = "/usr/local/bin/google-chrome"
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f'--user-agent={CUSTOM_HEADERS["User-Agent"]}')
    # Optionally add more headers with CDP if needed

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome( options=chrome_options)
    driver.fullscreen_window()
    return driver

def load_cookies(driver, cookies_file):
    if not os.path.exists(cookies_file):
        print("❌ Cookies file not found")
        return

    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    driver.get("https://khamsat.com/")  # open once before adding cookies
    driver.delete_all_cookies()
    for cookie in cookies:
        try:
           driver.add_cookie({
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", True),
                "httpOnly": cookie.get("httpOnly", False),
            })
           driver.refresh()
           print( driver.get_cookies())
        except Exception as e:
            print(e)
            print(f"⚠️ Skipped cookie {cookie['name']}: {e}")
    print(f"✅ Cookies loaded.{len(driver.get_cookies())}")

def keep_alive(driver):
    driver.get(TARGET_URL)
    print("🌍 Navigated to Khamsat with custom headers + cookies")

    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/service/create']"))
        )

        print("🔐 Logged in successfully!")
    except Exception as e:
        print("⚠️ Could not confirm login, maybe cookies expired?")
        # Send notification email about the failure
        try:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            subject = "Khamsat keep-alive: Login check failed"
            body = (
                f"Login confirmation failed at {now}.\n"
                f"URL: {TARGET_URL}\n"
                f"Error: {repr(e)}\n\n"
                "This usually indicates expired cookies. The script will still save debug_page.html/png if configured in main."
            )
            send_email_notification(subject, body)
        except Exception as inner_e:
            print(f"⚠️ Failed to trigger email notification: {inner_e}")

def main():
    global last_alert_unreads
    driver = setup_driver()
    last_alert_unreads = 0
    try:
        load_cookies(driver, COOKIES_FILE)
        keep_alive(driver)

        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("debug_page.png")
        print("💾 Saved debug_page.html + debug_page.png")
        # 🕰️ Get initial counter from khamsat page (like Date.now())
        try:
            counter = driver.execute_script("return Date.now();")
        except Exception:
            counter = int(time.time() * 1000)

        print(f"🧭 Initial Heartbeat Counter: {counter}")

        # 🔁 Continuous Heartbeat Loop (every 10s)
        while True:
            counter += 1
            hb_url = f"https://khamsat.com/ajax/account_stats?_={counter}"
            try:
                driver.get(hb_url)
                html = driver.page_source
                print(driver.page_source)
                print("🟢 Heartbeat Sent:", hb_url)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                pre_tag = soup.find("pre")

                if pre_tag:
                    json_text = pre_tag.get_text()
                    try:
                        data = json.loads(json_text)
                        unreads = data["unread_notifications_count"] + data["unread_messages_count"]
                        print("🔔 Unread Notifications:", data["unread_notifications_count"])
                        print("✉️ Unread Messages:", data["unread_messages_count"])
                        print("✉️ total Messages:", unreads)
                       
                        if unreads == 0:
                            last_alert_unreads = 0
                        if unreads > last_alert_unreads:
                            send_email_notification(
                                "Khamsat keep-alive: Unread Notifications",
                                f"Unread Notifications: {data['unread_notifications_count']}\n"
                                f"Unread Messages: {data['unread_messages_count']}\n"
                                f"Total Messages: {unreads}",
                            )
                            last_alert_unreads = unreads
                    except json.JSONDecodeError:
                        print("⚠️ JSON Decode Failed")
                else:
                    print("⚠️ No JSON in response")
            except Exception as e:
                print("⚠️ Heartbeat Failed:", e)

            time.sleep(10)
    finally:
        driver.quit()
        print("🛑 Driver closed")

if __name__ == "__main__":
    main()
