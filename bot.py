import os
import json
import random
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Load the cookies from your GitHub Secret
        cookies = json.loads(os.environ['GOOGLE_COOKIES'])
        
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        # Navigating as a verified user
        page.goto("https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform")
        
        # Click the 'Record Email' checkbox
        page.click('div[role="checkbox"]')

        # Submit random answer
        choice = random.choice(["A", "B", "C", "D", "E"])
        page.click(f"text={choice}")
        page.click("text=Submit")
        
        print(f"Cloud Success: Submitted {choice}")
        browser.close()
