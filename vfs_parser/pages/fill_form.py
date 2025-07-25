import os
import time
import sqlite3
import datetime

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


def fill_form(page):
    try:
        input_xpath = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[10]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        first_name_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[6]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        last_name_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[7]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        sex_dropdown_path = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[8]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
        sex_xpath = f'xpath://span[contains(text(),"{os.environ["SEX"]}")]'
        nationality_dropbox_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[9]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
        nationality_xpath = f'xpath://span[contains(text(),"{os.environ["NATIONALITY"]}")]'
        passport_year_xpath = f'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[11]/div/div/div/app-ngb-datepicker/div/div[2]/input'
        country_code_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[14]/div/div/div[2]/div[1]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        phone_number_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[14]/div/div/div[2]/div[2]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        email_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[15]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        button_submit_text_xpath = 'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button/span[2]'
        time.sleep(2)
        is_loader_hide(page)
        time.sleep(30)
        page.ele(
            first_name_xpath).input(
            os.environ['FIRST_NAME'])
        page.ele(last_name_xpath).input(
            os.environ['LAST_NAME'])
        page.ele(sex_dropdown_path).click()
        page.ele(sex_xpath).click()
        page.ele(nationality_dropbox_xpath).click()
        page.ele(nationality_xpath).click()
        time.sleep(2)
        page.run_js(f'''
            const input = document.evaluate("{input_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (input) {{
                input.disabled = false;
                input.removeAttribute('disabled');
                input.value = '';
            }}
        ''')
        time.sleep(2)
        page.ele(f'xpath:{input_xpath}').input(
            os.environ['PASSPORT_NUMBER'])
        page.ele(passport_year_xpath).input(
            os.environ['PASSPORT_YEAR'])
        page.ele(country_code_xpath).input(
            os.environ['COUNTRY_CODE'])
        page.ele(phone_number_xpath).input(
            os.environ['PHONE_NUMBER'])
        page.ele(email_xpath).input(
            os.environ['YOUR_EMAIL'])
        time.sleep(2)
        page.ele(button_submit_text_xpath).click()
    except Exception as e:
        log_error(str(e))
        raise