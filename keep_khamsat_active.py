import json
import os
import tempfile
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


COOKIES_FILE = "cookies.json"
TARGET_URL = "https://khamsat.com/"


def get_chrome_major_version():
    result = subprocess.run(
        ["/opt/google/chrome/chrome", "--version"],
        capture_output=True, text=True
    )
    version = result.stdout.strip().split()[2]
    return version.split(".")[0]


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    temp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    chrome_major = get_chrome_major_version()

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version=chrome_major).install()),
        options=options
    )
    return driver


def load_cookies(driver, cookies_file):
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file not found: {cookies_file}")
        return

    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    driver.get(TARGET_URL)
    for cookie in cookies:
        cookie_dict = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie.get("path", "/"),
            "secure": cookie.get("secure", True),
            "httpOnly": cookie.get("httpOnly", False),
        }
        try:
            driver.add_cookie(cookie_dict)
        except Exception as e:
            print(f"⚠️ Skipped cookie {cookie['name']}: {e}")

    print("✅ Cookies loaded.")


def keep_alive(driver):
    driver.get(TARGET_URL)
    print(f"🌍 Navigated to {TARGET_URL}")
    time.sleep(5)

    try:
        wait = WebDriverWait(driver, 10)
        selectors = [
            "a.hsoub-dropdown-item-link[href*='/user/qozeem']",
            "a.hsoub-menu-item-link[href*='/user/qozeem']",
        ]

        username_element = None
        for selector in selectors:
            try:
                username_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✅ Found user menu with selector: {selector}")
                break
            except Exception:
                continue

        if username_element:
            print("🎯 Session still active.")
        else:
            print("🛑 Could not find user menu → cookies likely expired.")

    except Exception as e:
        print(f"⚠️ Error while checking session: {e}")


def main():
    print("🚀 Script start.")
    driver = setup_driver()

    try:
        load_cookies(driver, COOKIES_FILE)
        keep_alive(driver)
    finally:
        driver.quit()
        print("🛑 Driver closed.")


if __name__ == "__main__":
    main()
