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
        cleaned_cookies = []
        for cookie in raw_cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                cookie['sameSite'] = "Lax"
            cleaned_cookies.append(cookie)

        context = browser.new_context()
        context.add_cookies(cleaned_cookies)
        page = context.new_page()

        try:
            url = "https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform"
            page.goto(url, wait_until="networkidle")
            
            # 1. Click the 'Record Email' checkbox
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            # 2. Pick a random choice A-E
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected choice: {choice}")

            # 3. Robust Submit Click
            # This looks for the primary blue button by its role, not just the text
            submit_button = page.locator('div[role="button"]:has-text("Submit")')
            submit_button.wait_for(state="visible", timeout=5000)
            submit_button.click()
            
            # 4. Verify Success Screen
            page.wait_for_load_state("networkidle")
            print(f"Final Page Title: {page.title()}")
            
            if "Your response has been recorded" in page.content():
                print("Confirmed: Form successfully submitted to Google.")
            else:
                print("Warning: Submission page not confirmed. Taking debug screenshot.")
                page.screenshot(path="submission_check.png")

        except Exception as e:
            print(f"Crashed with error: {e}")
            page.screenshot(path="error.png")
        
        browser.close()

if __name__ == "__main__":
    run()
