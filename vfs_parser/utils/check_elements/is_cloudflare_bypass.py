import random
import time
from typing import Tuple

from DrissionPage.errors import PageDisconnectedError, ElementNotFoundError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


def is_cloudflare_bypass(
        page,
        xpaths: Tuple[str, ...] = (
                '//iframe[contains(@src, "challenges.cloudflare")]',
                '//div[contains(@class, "cloudflare")]',
                '//div[@id="cf-challenge-wrapper"]',
                '//input[contains(@name, "cf_captcha")]',
                '//div[contains(text(), "Checking your browser")]',
                '//div[contains(text(), "Проверка браузера")]'
        ),
        max_wait: int = 60,
        poll_interval: float = 1.5,
        verbose: bool = True
) -> bool:

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type((PageDisconnectedError, ElementNotFoundError))
    )
    def _check_protection(xpath: str) -> bool:
        try:
            elem = page.ele(f'xpath:{xpath}', timeout=3)
            if elem:
                if verbose:
                    print(f"Cloudflare element detected: {xpath}")
                return True
            return False
        except Exception as e:
            if verbose:
                print(f"Cloudflare ERR {xpath}: {str(e)}")
            return False

    start_time = time.time()
    last_status = ""

    if verbose:
        print("Start check Cloudflare")

    if 'challenges.cloudflare.com' in page.url:
        if verbose:
            print("Cloudflare detected by URL")
        return False

    while time.time() - start_time < max_wait:
        try:
            cloudflare_detected = any(_check_protection(xpath) for xpath in xpaths)

            if not cloudflare_detected:
                if page.ele('xpath://iframe[contains(@src, "cloudflare.com")]', timeout=1):
                    cloudflare_detected = True

            if not cloudflare_detected:
                if verbose:
                    print("Cloudflare not detected")
                return True

            elapsed = int(time.time() - start_time)
            new_status = f"Cloudflare disappear for ({elapsed}/{max_wait})"

            if verbose and new_status != last_status:
                print(new_status)
                last_status = new_status

            if cloudflare_detected:
                if _try_bypass_cloudflare(page, verbose):
                    return True

            time.sleep(poll_interval + random.uniform(0, 0.7))

        except Exception as e:
            if verbose:
                print(f"main cycle ERR: {str(e)}")
            time.sleep(3)

    if verbose:
        print("Cloudflare dont disappear")
    return False


def _try_bypass_cloudflare(page, verbose: bool = True) -> bool:
    try:
        iframe = page.ele('xpath://iframe[contains(@src, "challenges.cloudflare.com")]', timeout=5)
        if not iframe:
            return False

        page.frame = iframe

        shadow_host = page.ele('xpath://div[contains(@class, "main-wrapper")]', timeout=3)
        if shadow_host:
            shadow_root = shadow_host.shadow_root
            checkbox = shadow_root.ele('xpath://input[@type="checkbox"]', timeout=3)
            if checkbox:
                checkbox.js_click()
                if verbose:
                    print("Cloudflare checkbox pass")

                for _ in range(10):
                    if not page.ele('xpath://iframe[contains(@src, "challenges.cloudflare.com")]', timeout=1):
                        if verbose:
                            print("Cloudflare success")
                        return True
                    time.sleep(1)

        return False

    except Exception as e:
        if verbose:
            print(f"Cloudflare ERR: {str(e)}")
        return False
    finally:
        page.frame = None
