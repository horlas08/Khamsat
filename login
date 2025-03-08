from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime

# Credentials (replace with your real email and password)
EMAIL = "qozeemmonsurudeen@gmail.com"
PASSWORD = "horlas082001"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional - remove this if testing locally
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ar")  # Arabic interface
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    print(f"[{datetime.datetime.now()}] Attempting daily login...")

    driver.get("https://accounts.hsoub.com/login?source=khamsat&locale=ar")
    time.sleep(5)

    try:
        email_input = None
        password_input = None

        # Try finding elements by both NAME and Placeholder (for Arabic)
        try:
            email_input = driver.find_element(By.NAME, "email")
        except:
            email_input = driver.find_element(By.XPATH, "//input[@placeholder='البريد الإلكتروني']")
        
        email_input.send_keys(EMAIL)

        try:
            password_input = driver.find_element(By.NAME, "password")
        except:
            password_input = driver.find_element(By.XPATH, "//input[@placeholder='كلمة المرور']")
        
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)

        print(f"[{datetime.datetime.now()}] Login successful!")
        time.sleep(10)

    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error during login: {e}")
        driver.quit()
        raise

def refresh_loop(driver):
    last_login_date = None
    print(f"[{datetime.datetime.now()}] Starting refresh loop...")

    while True:
        today = datetime.date.today()

        # Login once per day
        if last_login_date != today:
            login(driver)
            last_login_date = today

        # Visit homepage to stay active
        driver.get("https://khamsat.com/")
        print(f"[{datetime.datetime.now()}] Page refreshed.")
        time.sleep(600)  # Refresh every 10 minutes to simulate activity

def main():
    driver = setup_driver()

    try:
        refresh_loop(driver)
    except KeyboardInterrupt:
        print(f"[{datetime.datetime.now()}] Script interrupted. Closing.")
        driver.quit()
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Fatal error: {e}")
        driver.quit()

if __name__ == "__main__":
    main()
