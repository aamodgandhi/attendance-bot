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
            
            # 1. Handle the 'Record Email' checkbox
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            # 2. Select a random answer A-E
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected: {choice}")

            # 3. Targeted Submission
            # We use the internal Google ID for the submit button to ensure it fires
            submit_btn = page.locator('div[role="button"][jsname="M2Sae"]')
            submit_btn.scroll_into_view_if_needed()
            submit_btn.click(force=True) # force=True bypasses visibility/layering checks
            
            # 4. Success Verification
            # This waits up to 10 seconds for Google's confirmation text
            page.wait_for_selector('text="Your response has been recorded"', timeout=10000)
            print("Confirmed: Form successfully submitted to Google.")

        except Exception as e:
            print(f"Failed: {e}")
            page.screenshot(path="final_fail_screen.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
