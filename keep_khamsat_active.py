import time
import json
import os
import tempfile
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# ---------- CONFIG ----------
COOKIES_FILE = "cookies.json"
TARGET_URL = "https://khamsat.com/"
# ----------------------------


def get_chrome_major_version():
    """Get installed Chrome major version (e.g. 140)."""
    result = subprocess.run(
        ["/opt/google/chrome/chrome", "--version"],
        capture_output=True, text=True
    )
    version = result.stdout.strip().split()[2]  # e.g. "140.0.7339.80"
    return version.split(".")[0]  # "140"


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # unique temp user data dir (avoid session not created error)
    temp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    # auto-detect installed Chrome version
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

    driver.get(TARGET_URL)  # must open domain before adding cookies
    for cookie in cookies:
        cookie_dict = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie.get("path", "/"),
            "secure": cookie.get("secure", True),
            "httpOnly": cookie.get("httpOnly", False),
        }
        driver.add_cookie(cookie_dict)

    print("✅ Cookies loaded.")


def keep_alive(driver):
    driver.get(TARGET_URL)
    print(f"🌍 Navigated to {TARGET_URL}")
    time.sleep(5)

    # Example: check if user menu exists (indicating logged in)
    try:
        user_menu = driver.find_element(By.CSS_SELECTOR, ".user-menu")
        print("🔐 Logged in successfully, user menu found.")
    except Exception:
        print("⚠️ Could not find user menu, maybe cookies expired?")


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
