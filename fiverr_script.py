from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://accounts.hsoub.com/login?source=khamsat&locale=ar")

# Login
driver.find_element(By.NAME, "email").send_keys("qozeemmonsurudeen@gmail.com")
driver.find_element(By.NAME, "password").send_keys("horlas082001")
driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

time.sleep(10)
print("Logged in successfully")

# Refresh Fiverr every hour
while True:
    driver.get("https://www.fiverr.com/")
    print("Session refreshed")
    time.sleep(3600)  # 1 hour
