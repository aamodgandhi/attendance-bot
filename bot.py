import os
import json
import random
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        
        if not cookie_json:
            print("Error: GOOGLE_COOKIES secret not found!")
            return
            
        raw_cookies = json.loads(cookie_json)
        
        # --- CLEANING THE COOKIES ---
        cleaned_cookies = []
        for cookie in raw_cookies:
            # Playwright requires sameSite to be Strict, Lax, or None
            if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                cookie['sameSite'] = "Lax" # Defaulting to Lax fixes the crash
            cleaned_cookies.append(cookie)
        # --------------------------------------------------

        context = browser.new_context()
        context.add_cookies(cleaned_cookies)
        page = context.new_page()

        try:
            url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform"
            page.goto(url, wait_until="networkidle")
            
            print(f"Page Title: {page.title()}")
            
            # Interact with the form
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            page.click("span:text-is('Submit')")
            print(f"Success: Submitted {choice}")

        except Exception as e:
            print(f"Crashed with error: {e}")
            page.screenshot(path="error.png")
        
        browser.close()

if __name__ == "__main__":
    run()
