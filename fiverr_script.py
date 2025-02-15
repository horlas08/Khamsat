from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize WebDriver with error handling
try:
    print("🔄 Setting up WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"❌ WebDriverManager Error: {e}")
        exit(1)  # Exit if WebDriver fails to install

    print("✅ WebDriver setup complete!")

    # Open Khamsat login page
    driver.get("https://accounts.hsoub.com/login?source=khamsat&locale=ar")
    time.sleep(5)  # Wait for the page to load

    # Find and fill the email field
    try:
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys("your-email@example.com")
    except Exception as e:
        print(f"❌ Failed to locate email field: {e}")
        driver.quit()
        exit(1)

    # Find and fill the password field
    try:
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys("your-password")
        password_input.send_keys(Keys.RETURN)  # Press Enter
    except Exception as e:
        print(f"❌ Failed to locate password field: {e}")
        driver.quit()
        exit(1)

    time.sleep(5)  # Wait for login to process

    # Check if login was successful
    if "dashboard" in driver.current_url:
        print("✅ Login successful!")
    else:
        print("❌ Login failed. Check credentials or elements.")

except Exception as e:
    print(f"❌ Unexpected error: {e}")

finally:
    driver.quit()  # Close the browser
    print("🚪 WebDriver closed.")
