import os
import json
import random
import time
import requests
from playwright.sync_api import sync_playwright

def run():
    # Humanizing Delay
    delay = random.randint(60, 300) 
    print(f"Humanizing the bot: Waiting for {delay} seconds before starting...")
    time.sleep(delay)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        
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
            url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform?usp=header"
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

            # 3. Triple-Redundant Submission
            # We now look for the button by text first, then by internal ID
            submit_selectors = [
                'div[role="button"]:has-text("Submit")',
                'div[role="button"][jsname="M2Sae"]',
                'span:text-is("Submit")'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    print(f"Attempting submission with selector: {selector}")
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=5000):
                        btn.scroll_into_view_if_needed()
                        btn.click(force=True)
                        submitted = True
                        break
                except:
                    continue

            # Method B: The Nuclear Option (Direct JS Submit)
            if not submitted:
                print("UI buttons not found. Triggering JS Form Submit...")
                page.evaluate('document.forms[0].submit()')

            # 4. Final Verification and Notification
            page.wait_for_selector('text="Your response has been recorded"', timeout=15000)
            print("Confirmed: Submission successful.")

            if webhook_url:
                requests.post(webhook_url, json={
                    "content": f"✅ **Attendance Logged!**\n**Choice:** {choice}\n**Status:** Confirmed."
                })

        except Exception as e:
            print(f"Bot Error: {e}")
            page.screenshot(path="final_debug.png")
            if webhook_url:
                requests.post(webhook_url, json={"content": f"⚠️ **Bot Error:** {e}"})
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
