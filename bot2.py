import os
import json
import random
import time
import requests
from playwright.sync_api import sync_playwright

def run():
    # 1. Humanizing Delay
    delay = random.randint(1, 5)
    print(f"Humanizing the bot: Waiting for {delay} seconds before starting...")
    time.sleep(delay)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Pulling secrets from environment variables
        cookie_json = os.environ.get('GOOGLE_COOKIES_2')
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        raw_user_id = os.environ.get('DISCORD_USER_ID')
        
        # Health Checks: Check GitHub Console logs to see if these are 'Found'
        print(f"Secret Check: COOKIES={'Found' if cookie_json else 'Missing'}")
        print(f"Secret Check: WEBHOOK={'Found' if webhook_url else 'Missing'}")
        print(f"Secret Check: USER_ID={'Found' if raw_user_id else 'Missing'}")
        
        discord_user_id = f"<@{raw_user_id}>" if raw_user_id else ""

        if not cookie_json:
            print("Error: GOOGLE_COOKIES_2 secret not found!")
            return

        raw_cookies = json.loads(cookie_json)
        cleaned_cookies = [{**c, 'sameSite': 'Lax'} if c.get('sameSite') not in ["Strict", "Lax", "None"] else c for c in raw_cookies]

        context = browser.new_context()
        context.add_cookies(cleaned_cookies)
        page = context.new_page()

        try:
            url = "https://forms.office.com/Pages/ResponsePage.aspx?id=b35GRCxGok6CP3gA3lQ049-nlvMuF6NIt-MIux7DYXVUMTFKU1UzMkNXWUVORkpHMDZFVVROVFZJRi4u&origin=QRCode&sid=7417a3a4-3d80-44e5-be6a-4e092e626cdd"
            page.goto(url, wait_until="networkidle")

            # 2. Select a random option
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.get_by_role("radio", name=choice).click()
            print(f"Selected Choice: {choice}")

            # 3. Submit
            submit_btn = page.get_by_role("button", name="Submit")
            submit_btn.click(force=True)

            # 4. Verification
            # Matching the specific text found in your debug image
            page.wait_for_selector('text="Your answers have been submitted successfully"', timeout=15000)
            print("Confirmed: Microsoft Form submitted.")

            if webhook_url:
                print("Sending Discord notification...")
                requests.post(webhook_url, json={
                    "content": f"{discord_user_id} ✅ **Microsoft Attendance Logged!**\n**Choice:** {choice}"
                })
                time.sleep(2) # Give the network request a moment to clear

        except Exception as e:
            # Content-based late-sync check
            if "submitted successfully" in page.content():
                print("Confirmed: Submission succeeded via late-sync check.")
                if webhook_url:
                    requests.post(webhook_url, json={"content": f"{discord_user_id} ✅ **Attendance Logged!** (Verified via content check)"})
                    time.sleep(2)
            else:
                print(f"Bot Error: {e}")
                page.screenshot(path="final_debug.png")
                if webhook_url:
                    requests.post(webhook_url, json={"content": f"{discord_user_id} ⚠️ **Bot Error:** {e}"})
                    time.sleep(2)

        finally:
            browser.close()

if __name__ == "__main__":
    run()
