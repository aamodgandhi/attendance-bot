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
            
            # 1. Click 'Record Email'
            page.wait_for_selector('div[role="checkbox"]', timeout=10000)
            checkbox = page.query_selector('div[role="checkbox"]')
            if checkbox and checkbox.get_attribute('aria-checked') == 'false':
                checkbox.click()

            # 2. Pick random answer
            choice = random.choice(["A", "B", "C", "D", "E"])
            page.click(f"span:text-is('{choice}')")
            print(f"Selected choice: {choice}")

            # 3. Aggressive Submission using internal Google ID
            submit_selector = 'div[role="button"][jsname="M2Sae"]'
            page.wait_for_selector(submit_selector, state="visible", timeout=5000)
            page.click(submit_selector)
            
            # 4. Final verification
            page.wait_for_load_state("networkidle")
            if "Your response has been recorded" in page.content():
                print("Confirmed: Submission successful.")
            else:
                page.screenshot(path="failed_submit.png")
                print("Error: Submission page not confirmed.")

        except Exception as e:
            print(f"Crashed with error: {e}")
            page.screenshot(path="error.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    run()
