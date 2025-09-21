import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")        # headless mode for CI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ✅ unique temporary profile dir each GitHub Actions run
    temp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def keep_alive(driver):
    try:
        driver.get("https://khamsat.com/")  # your target URL
        print("Page title:", driver.title)

        # Example interaction: wait for search box
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            print("Search box found, sending keys...")
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys("test")
            search_box.send_keys(Keys.RETURN)
        except TimeoutException:
            print("Search box not found in time")

    except Exception as e:
        print("Error in keep_alive:", e)

def main():
    print("Script start.")
    driver = setup_driver()
    try:
        keep_alive(driver)
    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    main()
