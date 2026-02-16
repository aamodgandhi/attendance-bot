import os
import json
import random
import time
import requests
from playwright.sync_api import sync_playwright

def run():
    # 1. Humanizing Delay
    delay = random.randint(60, 300) 
    print(f"Humanizing the bot: Waiting for {delay} seconds...")
    time.sleep(delay)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        cookie_json = os.environ.get('GOOGLE_COOKIES')
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        
        if not cookie_json:
            print("Error: GOOGLE_COOKIES secret not found!")
            return
            
        raw_cookies = json.loads(cookie_json)
        cleaned_cookies = [{**c, 'sameSite': 'Lax'} if c.get('sameSite') not in ["Strict", "Lax", "None"] else c for c in raw_cookies]

        context = browser.new_context()
        context.add_cookies(cleaned_cookies)
        page = context.new_page()

        try:
            url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform?usp=header"
            page.goto(url, wait_until="networkidle")
            
            # 2. Checkbox and Answer Selection
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected: {choice}")

            # 3. Aggressive Submission
            submit_selector = 'div[role="button"][jsname="M2Sae"]'
            page.locator(submit_selector).click(force=True)
            
            # 4. Multi-Layer Verification
            # We check for the URL change OR the success text
            print("Verifying submission...")
            try:
                # Wait for the URL to contain 'formResponse'
                page.wait_for_url("**/formResponse", timeout=15000)
                success = True
            except:
                # Fallback: check if the success text exists in the page content
                success = "Your response has been recorded" in page.content()

            if success:
                print("Confirmed: Submission successful.")
                if webhook_url:
                    requests.post(webhook_url, json={
                        "content": f"✅ **Attendance Logged!**\n**Choice:** {choice}\n**Status:** Confirmed via URL sync."
                    })
            else:
                raise Exception("Could not verify success screen.")

        except Exception as e:
            # Check one last time before reporting an error
            if "formResponse" in page.url or "recorded" in page.content():
                print("Confirmed: Late sync successful.")
                if webhook_url:
                    requests.post(webhook_url, json={"content": f"✅ **Attendance Logged (Late Sync)!**\n**Choice:** {choice}"})
            else:
                print(f"Bot Error: {e}")
                page.screenshot(path="final_debug.png")
                if webhook_url:
                    requests.post(webhook_url, json={"content": f"⚠️ **Bot Error:** {e}"})
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
