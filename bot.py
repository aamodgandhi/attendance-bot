import os
import json
import random
import time
import requests # Required for Discord notifications
from playwright.sync_api import sync_playwright

def run():
    # 1. Humanizing Delay: Wait between 1 and 15 minutes
    # mimicking a student settling into class
    delay = random.randint(60, 900) 
    print(f"Humanizing the bot: Waiting for {delay} seconds before starting...")
    time.sleep(delay)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL') # Secret from GitHub
        
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
            # url = "https://docs.google.com/forms/d/e/1FAIpQLSey1HilfABtgyjfpxSnT28tPBsIDBco9nzG270MAO0AXbblvw/viewform"
            url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform?usp=header"
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
                # The Nuclear Option: Directly triggers the form's submit action
                page.evaluate('document.forms[0].submit()')

            # 5. Final Verification and Notification
            page.wait_for_selector('text="Your response has been recorded"', timeout=20000)
            print("Confirmed: Submission successful.")

            if webhook_url:
                payload = {
                    "username": "Attendance Bot",
                    "content": f"✅ **Attendance Logged!**\n**Account:** aamodg2@illinois.edu\n**Choice:** {choice}\n**Status:** Confirmed via success screen."
                }
                requests.post(webhook_url, json=payload)

        except Exception as e:
            error_msg = f"❌ **Bot Error:** {e}"
            print(error_msg)
            page.screenshot(path="final_debug.png")
            if webhook_url:
                requests.post(webhook_url, json={"content": error_msg})
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
