import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

load_dotenv('config/.env')


def send_email_notification(subject, message):
    try:
        # Настройки SMTP из переменных окружения
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        sender_email = os.getenv('SENDER_EMAIL')
        recipient_email = os.getenv('RECIPIENT_EMAIL')

        if not all([smtp_server, smtp_username, smtp_password, sender_email, recipient_email]):
            logging.error("Не все переменные окружения для SMTP настроены")
            return False

        # Создание сообщения
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Добавление текста сообщения
        msg.attach(MIMEText(message, 'plain'))

        # Установка соединения и отправка
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        logging.info("email send")
        return True

    except Exception as e:
        logging.error(f"email ERR: {str(e)}")
        return False