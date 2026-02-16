import os
import json
import random
import time
from playwright.sync_api import sync_playwright

def run():
    # 1. Humanizing Delay: Wait between 1 and 15 minutes
    # This ensures you don't submit at the exact same second every time
    delay = random.randint(60, 900) 
    print(f"Humanizing the bot: Waiting for {delay} seconds before starting...")
    time.sleep(delay)

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
            url = "https://docs.google.com/forms/d/e/1FAIpQLSey1HilfABtgyjfpxSnT28tPBsIDBco9nzG270MAO0AXbblvw/viewform"
            page.goto(url, wait_until="networkidle")
            
            # 2. Handle the 'Record Email' checkbox
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            # 3. Select a random answer
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected: {choice}")

            # 4. Triple-Redundant Submission
            submit_selector = 'div[role="button"][jsname="M2Sae"]'
            
            print("Attempting Method A: Scroll and Click...")
            btn = page.locator(submit_selector)
            btn.scroll_into_view_if_needed()
            btn.click(force=True, timeout=5000)
            
            time.sleep(3)
            if "Your response has been recorded" not in page.content():
                print("Method A failed. Attempting Method B: JS Form Submit...")
                # The Nuclear Option: Triggers the form's internal submit action
                page.evaluate('document.forms[0].submit()')

            # 5. Final Verification
            page.wait_for_selector('text="Your response has been recorded"', timeout=20000)
            print("Confirmed: Submission successful.")

        except Exception as e:
            print(f"Final Attempt Failed: {e}")
            page.screenshot(path="final_debug.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
