import random
import time
import os

from DrissionPage.errors import PageDisconnectedError

from utils.check_elements.is_cloudflare_bypass import is_cloudflare_bypass, _try_bypass_cloudflare


def login_to_vfs(page, max_attempts=3):

    def wait_random_delay():
        delay = random.uniform(1, 3)
        time.sleep(delay)
        return delay

    try:
        for attempt in range(1, max_attempts + 1):
            print(f"\nAttempt {attempt}/{max_attempts}")

            try:

                page.get("https://visa.vfsglobal.com/blr/ru/pol/dashboard", timeout=60)
                print(f"Waiting ({wait_random_delay():.1f})")


                if cookie_btn := page.ele('xpath://button[contains(., "Согласиться")]', timeout=10):
                    cookie_btn.click()
                    print(f"Cookies accepted ({wait_random_delay():.1f} сек)")

                # Ждем загрузки формы входа
                if page.ele('xpath://input[@id="email"]', timeout=15):
                    page.ele('xpath://input[@id="email"]').input(os.getenv('YOUR_EMAIL', ''))
                    wait_random_delay()

                    page.ele('xpath://input[@id="password"]').input(os.getenv('PASSWORD', ''))
                else:
                    print("Email field not found, trying alternative selectors...")
                    # Попробуем другие селекторы
                    email_field = page.ele('css:input[type="email"]', timeout=5) or page.ele('css:input[name="email"]', timeout=5)
                    if email_field:
                        email_field.input(os.getenv('YOUR_EMAIL', ''))
                        wait_random_delay()
                        
                        pwd_field = page.ele('css:input[type="password"]', timeout=5) or page.ele('css:input[name="password"]', timeout=5)
                        if pwd_field:
                            pwd_field.input(os.getenv('PASSWORD', ''))
                    else:
                        print("No email/password fields found")
                        continue
                wait_random_delay()

                if is_cloudflare_bypass(page, verbose=True):
                    print("Cloudflare pass")

                _try_bypass_cloudflare(page)

                page.ele('xpath://button[@type="submit"]').click()

                if page.ele('xpath://*[contains(text(), "Dashboard")]', timeout=30):
                    print("Success!")
                    return True

            except PageDisconnectedError:
                print("Connection ERR")
                if attempt == max_attempts:
                    raise
                time.sleep(5 * attempt)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise