import json
import os
import time
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

def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/local/bin/google-chrome"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f'--user-agent={CUSTOM_HEADERS["User-Agent"]}')
    # Optionally add more headers with CDP if needed

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def load_cookies(driver, cookies_file):
    if not os.path.exists(cookies_file):
        print("❌ Cookies file not found")
        return

    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    driver.get("https://khamsat.com/")  # open once before adding cookies
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
        except Exception as e:
            print(f"⚠️ Skipped cookie {cookie['name']}: {e}")
    print("✅ Cookies loaded.")

def keep_alive(driver):
    driver.get(TARGET_URL)
    print("🌍 Navigated to Khamsat with custom headers + cookies")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/user/']"))
        )
        print("🔐 Logged in successfully!")
    except Exception:
        print("⚠️ Could not confirm login, maybe cookies expired?")

def main():
    print("🚀 Script start")
    driver = setup_driver()
    try:
        load_cookies(driver, COOKIES_FILE)
        keep_alive(driver)

        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("debug_page.png")
        print("💾 Saved debug_page.html + debug_page.png")
    finally:
        driver.quit()
        print("🛑 Driver closed")

if __name__ == "__main__":
    main()
