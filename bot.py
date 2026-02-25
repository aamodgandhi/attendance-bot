import os
import json
import random
import time
import requests
from playwright.sync_api import sync_playwright

def run():
    # Humanizing Delay
    delay = random.randint(60, 300) 
    print(f"Humanizing the bot: Waiting for {delay} seconds...")
    time.sleep(0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        
		# Pulls your ID from the GitHub Secret
        raw_user_id = os.environ.get('DISCORD_USER_ID')
        discord_user_id = f"<@{raw_user_id}>" if raw_user_id else ""									  
													   		
        if not cookie_json:
            print("Error: GOOGLE_COOKIES secret not found!")
            return
            
																			 
        raw_cookies = json.loads(cookie_json)
        cleaned_cookies = [{**c, 'sameSite': 'Lax'} if c.get('sameSite') not in ["Strict", "Lax", "None"] else c for c in raw_cookies]

        context = browser.new_context()
        context.add_cookies(cleaned_cookies)
        page = context.new_page()

        try:
            url = "https://docs.google.com/forms/d/e/1FAIpQLSey1HilfABtgyjfpxSnT28tPBsIDBco9nzG270MAO0AXbblvw/viewform"
            page.goto(url, wait_until="networkidle")
            
            # 1. Selection Logic
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected: {choice}")

            # 2. Redundant Submission Methods
            submit_selector = 'div[role="button"][jsname="M2Sae"]'
            
            # Method A: Standard Click with short timeout
            try:
                print("Attempting Method A: Standard Click...")
                page.locator(submit_selector).click(force=True, timeout=5000)
            except:
                pass

            # Method B: Direct JS Click if still on the form
            if "formResponse" not in page.url:
                try:
                    print("Attempting Method B: JS Button Click...")
                    page.evaluate(f'document.querySelector(\'{submit_selector}\').click()')
                except:
                    pass

            # Method C: The Nuclear Option (Direct Form Submit)
            if "formResponse" not in page.url:
                print("Attempting Method C: Direct Form Submit...")
                page.evaluate('document.forms[0].submit()')

            # 3. Final Verification
            time.sleep(5) # Allow redirect to clear
            if "formResponse" in page.url or "recorded" in page.content():
                print("Confirmed: Submission successful.")
                if webhook_url:
                    payload = {
                        "content": f"{discord_user_id} ✅ **Attendance Logged!**\n**Choice:** {choice}\n**Status:** Synced."
                    }
                    requests.post(webhook_url, json=payload)
															
            else:
                raise Exception("Verification failed: Success screen not reached.")

        except Exception as e:
            # Post-crash check: Did it succeed anyway?
            if "formResponse" in page.url or "recorded" in page.content():
                print("Confirmed: Late-sync success despite error.")
                if webhook_url:
                    requests.post(webhook_url, json={"content": f"{discord_user_id} ✅ **Attendance Logged (Late Sync)!**"})
            else:
                print(f"Bot Error: {e}")
                page.screenshot(path="final_debug.png")
                if webhook_url:
                    requests.post(webhook_url, json={"content": f"{discord_user_id} ⚠️ **Bot Error:** {e}"})
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
