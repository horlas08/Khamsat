#!/usr/bin/env python3
"""
Keep Khamsat active by loading cookies exported from your browser.
Place cookies.json (list of cookie dicts) next to this script.

Example cookie entry:
{
  "name": "session",
  "value": "abcd1234",
  "domain": ".khamsat.com",
  "path": "/",
  "expiry": 1735689600,
  "httpOnly": False,
  "secure": False
}
"""

import json
import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

COOKIES_FILE = "cookies.json"
REFRESH_INTERVAL_SECONDS = 600  # 10 minutes

def load_cookies_from_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cookies file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    if not isinstance(cookies, list):
        raise ValueError("cookies.json must contain a JSON array (list) of cookie objects.")
    return cookies

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # use new headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ar")
    # If running in CI and Chrome binary installed to /usr/local/bin/google-chrome explicitly:
    options.binary_location = "/usr/local/bin/google-chrome"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver

def add_cookies_to_driver(driver, cookies, base_url="https://khamsat.com"):
    # We must be on the domain before adding cookies
    driver.get(base_url)
    time.sleep(2)
    for c in cookies:
        cookie = {}
        # Required fields for Selenium: 'name' and 'value' plus optional domain/path/expiry/httpOnly/secure
        cookie["name"] = c.get("name")
        cookie["value"] = c.get("value")
        if "domain" in c and c["domain"]:
            cookie["domain"] = c["domain"]
        if "path" in c:
            cookie["path"] = c["path"]
        # Selenium expects 'expiry' to be int (seconds since epoch) if present
        if "expiry" in c and c["expiry"] is not None:
            try:
                cookie["expiry"] = int(c["expiry"])
            except Exception:
                pass
        if "httpOnly" in c:
            cookie["httpOnly"] = bool(c["httpOnly"])
        if "secure" in c:
            cookie["secure"] = bool(c["secure"])
        try:
            # Some cookies define hostOnly or other props that Selenium won't accept; use only allowed keys
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Could not add cookie {cookie.get('name')}: {e}")

def refresh_loop(driver, interval_seconds=REFRESH_INTERVAL_SECONDS):
    print(f"[{datetime.datetime.now()}] Starting refresh loop. Refresh every {interval_seconds} seconds.")
    try:
        while True:
            driver.get("https://khamsat.com/")
            print(f"[{datetime.datetime.now()}] Visited khamsat.com (keep-alive).")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print(f"[{datetime.datetime.now()}] Interrupted by user. Exiting.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in refresh loop: {e}")
    finally:
        driver.quit()

def main():
    print(f"[{datetime.datetime.now()}] Script start.")
    cookies = load_cookies_from_file(COOKIES_FILE)
    driver = setup_driver()
    try:
        add_cookies_to_driver(driver, cookies)
        # After adding cookies, reload so the site sees the cookies
        driver.get("https://khamsat.com/")
        time.sleep(5)
        # Optionally check if logged in by searching for an element visible only when logged in
        # (left as optional - no failure if not found)
        refresh_loop(driver)
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Fatal error: {e}")
        driver.quit()

if __name__ == "__main__":
    main()
