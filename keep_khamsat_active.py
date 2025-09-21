import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def keep_khamsat_active():
    print("🚀 Script start.")

    # --- Setup headless Chrome ---
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        # --- Load cookies ---
        try:
            with open("khamsat_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
            driver.get("https://khamsat.com/")  # must open before adding cookies
            for cookie in cookies:
                if "sameSite" in cookie:
                    if cookie["sameSite"] == "None":
                        cookie["sameSite"] = "Strict"
                driver.add_cookie(cookie)
            print("✅ Cookies loaded.")
        except FileNotFoundError:
            print("❌ No cookie file found (khamsat_cookies.pkl). Please log in and save cookies first.")
            return

        # --- Reload after cookies ---
        driver.get("https://khamsat.com/")
        print("🌍 Navigated to https://khamsat.com/")

        # --- Wait and check for username ---
        selectors = [
            'a.hsoub-dropdown-item-link[href="/user/qozeem"]',
            'a.hsoub-menu-item-link[href="/user/qozeem"]'
        ]

        user_found = False
        for selector in selectors:
            try:
                user_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print("✅ Logged in as:", user_link.text.strip())
                user_found = True
                break
            except:
                continue

        if not user_found:
            print("⚠️ Could not find user menu — maybe cookies expired?")

    finally:
        driver.quit()
        print("🛑 Driver closed.")

if __name__ == "__main__":
    keep_khamsat_active()
