import asyncio
import logging
import sqlite3
import datetime
import logger
from __main__ import monitoring_flags
from config.page.page import VisaOpenPage
from pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from pages.login import login_to_vfs
from vfs_parser.utils.email.send_mail import send_email_notification

#from pyvirtualdisplay import Display
import subprocess
import time


async def background_monitoring():
    while monitoring_flags.get("USER ID", False):
        try:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, monitoring)
            except Exception as e:
                error_msg = f"monitoring err: {str(e)}"
                logger.error(error_msg)
                send_email_notification("VFS monitoring err", error_msg)

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
        #display = Display(size=(1920, 1080))
        #display.start()
        page = VisaOpenPage.create()
        login_to_vfs(page)
        check_dates_for_all_visa_types_for_one_city(page)
        #display.stop()
    except Exception as e:
        print("Error")
        #log_error(str(e))
        raise

while(True):
    monitoring()
