import os
import json
import random
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        
        if not cookie_json:
            print("Error: GOOGLE_COOKIES secret not found!")
            return
            
        raw_cookies = json.loads(cookie_json)
        cleaned_cookies = [
            {**c, 'sameSite': 'Lax'} if c.get('sameSite') not in ["Strict", "Lax", "None"] else c 
            for c in raw_cookies
        ]

        context = browser.new_context()
        context.add_cookies(cleaned_cookies)
        page = context.new_page()

        try:
            url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform"
            page.goto(url, wait_until="networkidle")
            
            # 1. Handle the 'Record Email' checkbox
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            # 2. Select a random answer
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected: {choice}")

            # 3. Enhanced Redundant Submission
            # Increased timeout to 15s to prevent the timeout error
            submit_selector = 'div[role="button"]:has-text("Submit")' 
            
            print("Waiting for submit button and scrolling...")
            submit_btn = page.locator(submit_selector)
            submit_btn.scroll_into_view_if_needed()
            submit_btn.wait_for(state="visible", timeout=15000)

            # Method A: Standard Click
            print("Attempting Method A: Click...")
            submit_btn.click(force=True)
            
            # Method B: JavaScript Trigger (Redundancy)
            time.sleep(3)
            if "Your response has been recorded" not in page.content():
                print("Method A likely failed. Attempting Method B: JS Click...")
                page.evaluate('document.querySelector(\'div[role="button"][jsname="M2Sae"]\').click()')

            # 4. Final Verification
            page.wait_for_selector('text="Your response has been recorded"', timeout=10000)
            print("Confirmed: Submission successful.")

        except Exception as e:
            print(f"Failed at step: {e}")
            page.screenshot(path="timeout_debug.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
