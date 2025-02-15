from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove this line to see browser window
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# Start Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open Khamsat login page
driver.get("https://accounts.hsoub.com/login?source=khamsat&locale=ar")

try:
    # Wait for the email field
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_field.send_keys("qozeemmonsurudeen@gmail.com")  # Change this

    # Wait for the password field
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "horlas082001"))
    )
    password_field.send_keys("your-password")  # Change this

    # Click the login button
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تسجيل الدخول')]"))
    )
    login_button.click()

    # Wait for login to complete
    time.sleep(5)

    # Print session cookies
    cookies = driver.get_cookies()
    print("Logged in successfully. Session cookies:", cookies)

except Exception as e:
    print("Login failed:", e)

# Keep session alive
while True:
    print("Keeping Khamsat session alive...")
    time.sleep(300)  # Refresh session every 5 minutes
    driver.refresh()
