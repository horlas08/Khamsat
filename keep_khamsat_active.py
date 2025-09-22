import json
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIES_FILE = "cookies.json"
TARGET_URL = "https://khamsat.com/"

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=options, headless=True)
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

    selectors = [
        'a.hsoub-dropdown-item-link[href="/user/qozeem"]',
        'a.hsoub-menu-item-link[href="/user/qozeem"]',
    ]

    found = False
    for selector in selectors:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print("🔐 Logged in successfully, user element found.")
            found = True
            break
        except Exception:
            print(f"❌ Selector not found: {selector}")
            continue

    if not found:
        print("⚠️ Could not find user element, maybe cookies expired?")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("debug_page.png")
        print("💾 Saved page HTML to debug_page.html")
        print("📸 Screenshot saved to debug_page.png")

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
