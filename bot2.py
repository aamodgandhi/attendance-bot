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
        # Pulling from the requested GOOGLE_COOKIES_2 secret
        cookie_json = os.environ.get('GOOGLE_COOKIES_2')
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        raw_user_id = os.environ.get('DISCORD_USER_ID')
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
            # Using the provided ECE 110 Microsoft Form URL
            url = "https://forms.office.com/Pages/ResponsePage.aspx?id=b35GRCxGok6CP3gA3lQ049-nlvMuF6NIt-MIux7DYXVUMTFKU1UzMkNXWUVORkpHMDZFVVROVFZJRi4u&origin=QRCode&sid=7417a3a4-3d80-44e5-be6a-4e092e626cdd"
            page.goto(url, wait_until="networkidle")

            # 2. Select a random option
            # Using get_by_role("radio") fixes the strict mode violation error
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.get_by_role("radio", name=choice).click()
            print(f"Selected Choice: {choice}")

            # 3. Submit
            submit_btn = page.get_by_role("button", name="Submit")
            submit_btn.click(force=True)

            # 4. Verification
            page.wait_for_selector('text="Your response was submitted"', timeout=15000)
            print("Confirmed: Microsoft Form submitted.")

            if webhook_url:
                requests.post(webhook_url, json={
                    "content": f"{discord_user_id} ✅ **Microsoft Attendance Logged!**\n**Choice:** {choice}"
                })

        except Exception as e:
            print(f"Bot Error: {e}")
            page.screenshot(path="final_debug.png")
            if webhook_url:
                requests.post(webhook_url, json={"content": f"{discord_user_id} ⚠️ **Bot Error:** {e}"})

        finally:
            browser.close()

if __name__ == "__main__":
    run()
