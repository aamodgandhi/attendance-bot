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

            # --- REDUNDANT SUBMISSION BLOCK ---
            submit_selector = 'div[role="button"][jsname="M2Sae"]'
            
            # Method A: Forced Click (Standard)
            print("Attempting Method A: Forced Click...")
            page.click(submit_selector, force=True, timeout=5000)
            
            # Method B: JavaScript Trigger (Bypasses UI layers)
            time.sleep(2)
            if "Your response has been recorded" not in page.content():
                print("Method A failed. Attempting Method B: JS Click...")
                page.evaluate(f'document.querySelector(\'{submit_selector}\').click()')

            # Method C: Keyboard Simulation (Direct focus submission)
            time.sleep(2)
            if "Your response has been recorded" not in page.content():
                print("Method B failed. Attempting Method C: Keyboard Enter...")
                page.focus(submit_selector)
                page.keyboard.press("Enter")

            # 4. Success Verification
            page.wait_for_load_state("networkidle")
            if "Your response has been recorded" in page.content():
                print("Confirmed: Submission successful.")
            else:
                page.screenshot(path="final_fail_screen.png")
                print("Error: All submission methods failed.")

        except Exception as e:
            print(f"System Crash: {e}")
            page.screenshot(path="error.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
