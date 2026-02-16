import os
import json
import random
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # 1. Launch a headless browser in the cloud
        browser = p.chromium.launch(headless=True)
        
        # 2. Parse the encrypted cookies from your Repository Secret
        # This allows the cloud bot to 'become' aamodg2@illinois.edu
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        if not cookie_json:
            print("Error: GOOGLE_COOKIES secret not found!")
            return
            
        cookies = json.loads(cookie_json)
        
        # 3. Create a browser context and inject your verified session
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        # 4. Navigate to your attendance form
        url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform"
        page.goto(url)
        
        # 5. Wait for the 'Record Email' checkbox and click it
        # This mimics the manual interaction that Apps Script couldn't do
        page.wait_for_selector('div[role="checkbox"]')
        checkbox = page.query_selector('div[role="checkbox"]')
        if checkbox and checkbox.get_attribute('aria-checked') == 'false':
            checkbox.click()
            print("Verified email checkbox clicked.")

        # 6. Pick a random choice A-E and submit
        choice = random.choice(["A", "B", "C", "D", "E"])
        # We find the span with the letter and click it
        page.click(f"span:text-is('{choice}')")
        
        # 7. Final Submission
        page.click("span:text-is('Submit')")
        print(f"Success: Attendance submitted with choice {choice}")
        
        browser.close()

if __name__ == "__main__":
    run()
