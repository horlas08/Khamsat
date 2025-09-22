import json
import os
import tempfile
import subprocess
import time
import requests
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


def debug_page(driver, selectors=None, save_prefix="debug"):
    """Debug helper: save HTML, screenshot, cookies, and requests output."""
    if selectors is None:
        selectors = [
            'a.hsoub-dropdown-item-link[href^="/user/"]',
            'a.hsoub-menu-item-link[href^="/user/"]',
        ]

    time.sleep(2)

    # Save full HTML
    html_path = f"{save_prefix}_page.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source or "")
    print(f"💾 Saved page HTML to {html_path}")

    # Screenshot
    png_path = f"{save_prefix}_page.png"
    try:
        driver.save_screenshot(png_path)
        print(f"📸 Screenshot saved to {png_path}")
    except Exception as e:
        print("⚠️ Screenshot failed:", e)

    # Cookies
    try:
        print("🍪 Current cookies:", driver.get_cookies())
    except Exception as e:
        print("⚠️ Could not get cookies:", e)

    # Try selectors
    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            outer = driver.execute_script("return arguments[0].outerHTML;", el)
            print(f"✅ Found element for selector {sel}: {outer}")
        except Exception:
            print(f"❌ Selector not found: {sel}")

    # Also test with requests
    try:
        sess = requests.Session()
        for c in driver.get_cookies():
            sess.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path", "/"))
        resp = sess.get(TARGET_URL)
        req_html = f"{save_prefix}_requests.html"
        with open(req_html, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"🌐 requests GET {resp.status_code}, saved to {req_html}")
    except Exception as e:
        print("⚠️ requests check failed:", e)


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
            continue

    if not found:
        print("⚠️ Could not find user element, maybe cookies expired?")
        debug_page(driver, selectors=selectors)


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
