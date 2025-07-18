import random
import time
import os
from datetime import datetime
from DrissionPage import ChromiumPage
from dotenv import load_dotenv
from database import save_user

load_dotenv()



class SlotBooker:
    def __init__(self, page: ChromiumPage):
        self.page = page
        self.delay = random.uniform(1, 3)
        self.base_url = "https://visa.vfsglobal.com/blr/ru/pol"

    def check_and_book_slots(self) -> bool:
        """Основная функция проверки и бронирования"""
        try:
            self.page.get(f"{self.base_url}/dashboard")

            if not self._login():
                return False

            available_dates = self._check_available_dates()
            if not available_dates:
                return False

            return self._book_slot(available_dates[0])

        except Exception as e:
            print(f"Booking error: {str(e)}")
            return False

    def _login(self) -> bool:
        """Авторизация на сайте"""
        try:
            self.page.ele("#email").input(os.environ.get('YOUR_EMAIL', ''))
            self.page.ele("#password").input(os.environ.get('PASSWORD', ''))
            self.page.ele("xpath://button[@type='submit']").click()
            time.sleep(5)
            return True
        except:
            return False

    def _check_available_dates(self) -> list:
        """Проверка доступных дат"""
        try:
            self.page.get(f"{self.base_url}/appointment")
            dates = self.page.eles("xpath://td[contains(@class, 'available')]")
            return [date.text for date in dates]
        except:
            return []

    def _book_slot(self, date: str) -> bool:
        """Бронирование слота"""
        try:
            self.page.ele(f"xpath://td[text()='{date}']").click()
            time.sleep(2)

            # Заполнение формы
            form_data = {
                'first_name': os.environ.get('FIRST_NAME', ''),
                'last_name': os.environ.get('LAST_NAME', ''),
                'passport': os.environ.get('PASSPORT_NUMBER', '')
            }

            for field, xpath in FORM_FIELDS.items():
                self.page.ele(xpath).input(form_data[field])
                time.sleep(self.delay)

            # Подтверждение
            self.page.ele("xpath://button[contains(text(), 'Подтвердить')]").click()
            time.sleep(5)

            # Сохранение данных
            save_user(1, "", booking_date=date, visa_type=os.environ.get('VISA_CATEGORY', ''), confirmation_code=self._get_confirmation_code())

            return True
        except:
            return False

    def _get_confirmation_code(self) -> str:
        """Получение кода подтверждения"""
        try:
            return self.page.ele("xpath://div[@class='confirmation-code']").text
        except:
            return "UNKNOWN"


# Локаторы формы
FORM_FIELDS = {
    'first_name': "xpath://input[@id='firstName']",
    'last_name': "xpath://input[@id='lastName']",
    'passport': "xpath://input[@id='passportNumber']"
}