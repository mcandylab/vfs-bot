import asyncio
import logging
import sqlite3
import datetime
from config.page.page import VisaOpenPage
from pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from pages.login import login_to_vfs
from utils.email.send_mail import send_email_notification

#from pyvirtualdisplay import Display
import subprocess
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_error(error_message):
    now = datetime.datetime.now()
    with sqlite3.connect('database.db') as conn:
        conn.execute(
            'UPDATE metrics SET errors = errors + 1, last_updated = ? WHERE id = (SELECT id FROM metrics ORDER BY last_updated DESC LIMIT 1)',
            (now.isoformat(),)
        )
        conn.commit()
    logging.error(f"ERR: {error_message}")


def monitoring():
    try:
        print("Starting monitoring...")
        #display = Display(size=(1920, 1080))
        #display.start()
        page = VisaOpenPage.create()
        print("Page created, attempting login...")
        login_to_vfs(page)
        print("Login successful, checking dates...")
        check_dates_for_all_visa_types_for_one_city(page)
        print("Monitoring cycle completed")
        #display.stop()
    except Exception as e:
        print(f"Error in monitoring: {str(e)}")
        #log_error(str(e))
        raise

print("Starting VFS monitoring service...")
while(True):
    monitoring()
    print("Sleeping for 30 seconds...")
    time.sleep(30)
