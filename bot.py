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

            # 3. Aggressive Submission
            # This targets the specific Google Form submit button structure
            submit_selector = 'div[role="button"][jsname="M2Sae"]'
            page.wait_for_selector(submit_selector, state="visible", timeout=5000)
            page.click(submit_selector)
            
            # 4. Wait for the page to change to the confirmation screen
            page.wait_for_load_state("networkidle")
            
            # Check for the confirmation text specifically
            if "Your response has been recorded" in page.content():
                print("Confirmed: Submission successful.")
            else:
                # Take a screenshot if we are still on the form
                page.screenshot(path="failed_submit.png")
                print("Error: Still on the form. Submission did not trigger.")

        except Exception as e:
            print(f"Crashed: {e}")
            page.screenshot(path="error.png")
