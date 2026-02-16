import random
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch a real browser in the cloud
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1. Go to the form
        page.goto("https://docs.google.com/forms/d/e/1FAIpQLScyoEYQne1Zt273Hrlqx57qUALeL0CrNjn-iL-boUTqzOlFEg/viewform")

        # 2. Handle login if prompted (GitHub Actions starts fresh)
        # This part depends on your specific UIUC login flow.
        # Often, you can just use a saved Session Cookie (exported from Chrome) 
        # to skip the login screen entirely.

        # 3. Click the 'Record Email' checkbox
        page.click('div[role="checkbox"]')

        # 4. Pick a random choice A-E
        choice = random.choice(["A", "B", "C", "D", "E"])
        page.click(f"text={choice}")

        # 5. Submit
        page.click("text=Submit")
        print(f"Successfully submitted {choice}")
        browser.close()

if __name__ == "__main__":
    run()
