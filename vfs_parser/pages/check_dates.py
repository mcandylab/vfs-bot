import os
import sqlite3
import datetime

from DrissionPage._functions.keys import Keys

from utils.check_elements.is_cloudflare_bypass import is_cloudflare_bypass
from utils.check_elements.is_loader_hide import is_loader_hide

def log_error(error_message):
    now = datetime.datetime.now()
    with sqlite3.connect('database.db') as conn:
        conn.execute(
            'UPDATE metrics SET errors = errors + 1, last_updated = ? WHERE id = (SELECT id FROM metrics ORDER BY last_updated DESC LIMIT 1)',
            (now.isoformat(),)
        )
        conn.commit()
    print(f"ERR: {error_message}")


def check_dates(page):
    try:
        page.ele(
            'xpath:/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[1]/div[2]/button', timeout=60).input(
            Keys.ENTER)

        is_loader_hide(page)

        page.ele('xpath://*[@id="mat-select-value-1"]/span').click()
        page.ele(f'xpath://span[contains(text(),"Poland Visa Application Center-{os.environ["CITY"]}")]').click()

        is_loader_hide(page)

        page.ele(
            'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[2]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span').click()
        page.ele(f'xpath://span[contains(text(), "{os.environ["VISA_CATEGORY"]}")]').click()

        is_loader_hide(page)

        page.scroll.down(600)
        page.ele(
            'xpath:/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[3]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span').click()
        page.ele(f'xpath://span[contains(text(),"{os.environ["VISA_SUBCATEGORY"]}")]').click()

        is_loader_hide(page)

        page.ele(
            'css:body > app-root > div > main > div > app-eligibility-criteria > section > form > mat-card.mat-mdc-card.mdc-card.form-card.ng-star-inserted > form > div:nth-child(7) > div.datepicker-div.form-group > input').input(
            os.environ['BIRTH_DAY'])
        page.close()
    except Exception as e:
        log_error(str(e))
        raise