
import DrissionPage
import random
from dotenv import load_dotenv
import os
import sys
import logging
sys.stdout.reconfigure(encoding='utf-8')

# Установить UTF-8 для консоли
os.environ["PYTHONIOENCODING"] = "utf-8"

# Настроить логирование в файл
logging.basicConfig(filename="error.log", level=logging.DEBUG, encoding="utf-8")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

class VisaOpenPage:
    @staticmethod
    def create(base_url='https://visa.vfsglobal.com/blr/ru/pol/dashboard'):
        try:
            logging.info("Browser init.")
            options = DrissionPage.ChromiumOptions()

            # options.set_browser_path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

            # options.set_user_data_path(r"C:\Users\user\AppData\Local\Temp\edge_profile")

            # # Указать порт отладки
            # options.set_argument("--remote-debugging-port=9222")

            # options.incognito(True)
            # options.set_argument("--no-sandbox")
            # options.set_argument("--lang=en-US,en")
            # options.set_argument("--disable-gpu")
            # options.set_argument("--single-process")
            # options.set_argument("--disable-web-security")
            # options.set_argument("--disable-dev-shm-usage")
            # # options.set_argument("--headless=new")
            # options.set_argument("--disable-blink-features=AutomationControlled")
            # options.set_argument(f"--user-agent={random.choice(USER_AGENTS)}")


            options = DrissionPage.ChromiumOptions()
            
            # Docker/Linux configuration для AMD64
            options.set_browser_path("/usr/bin/google-chrome-stable")
            options.set_user_data_path("/tmp/chrome_profile")
            options.set_argument("--headless=new")
            options.set_argument("--no-sandbox")
            options.set_argument("--disable-dev-shm-usage")
            options.set_argument("--disable-gpu")
            options.set_argument("--disable-web-security")
            options.set_argument("--disable-features=VizDisplayCompositor")
            options.set_argument("--disable-extensions")
            options.set_argument("--disable-plugins")
            options.set_argument("--window-size=1920,1080")
            options.set_argument("--lang=en-US,en")
            options.set_argument("--disable-blink-features=AutomationControlled")
            options.set_argument(f"--user-agent={random.choice(USER_AGENTS)}")
            options.set_argument("--remote-debugging-port=9222")

            if 'PROXY_SERVER' in os.environ:
                options.set_argument(f"--proxy-server={os.environ['PROXY_SERVER']}")
                logging.info(f"Proxy: {os.environ['PROXY_SERVER']}")
            else:
                logging.info("Not proxy")
                print("Not proxy")

            logging.info("ChromiumPage add")
            page = DrissionPage.ChromiumPage(addr_or_opts=options)
            load_dotenv('config/.env')

            page.base_url = base_url
            logging.info("Success")
            return page

        except DrissionPage.errors.BrowserConnectError as e:
            logging.error(f"Connection browser ERR: {str(e)}")
            print(f"Connection browser ERR: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"page ERR: {str(e)}")
            print(f"page ERR: {str(e)}")
            raise