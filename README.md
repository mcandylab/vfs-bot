# VFS-Global

# Инструкция по запуску сайта (Flask)

1. **Установите Python 3.10+**  
   Скачать: https://www.python.org/downloads/

2. **Создайте и активируйте виртуальное окружение:**
   ```
   python -m venv venv
   # Для Windows:
   venv\Scripts\activate
   # Для Linux/Mac:
   source venv/bin/activate
   ```

3. **Установите зависимости:**
   ```
   pip install -r requirements.txt
   ```

4. **Запустите Flask-приложение:**
   ```
   cd site
   python app.py
   ```

5. **Откройте сайт в браузере:**
   - Главная страница: http://127.0.0.1:5000/dashboard


---

# Инструкция по запуску Telegram-бота

1. **Убедитесь, что активировано виртуальное окружение и установлены зависимости (см. выше).**

2. **Укажите токен бота в файле `tg-bot.py`:**
   ```python
   BOT_TOKEN = 'ВАШ_ТОКЕН_ТУТ'
   ```

3. **Запустите бота:**
   ```
   python tg-bot.py
   ```


---

# Как запустить сайт и бота на сервере (Linux)

1. **Установите Python 3.10+ и необходимые пакеты (см. выше).**

2. **Запустите сайт с помощью `nohup` (работа в фоне):**
   ```
   cd /path/to/VFS-Global/site
   nohup python app.py > ../site.log 2>&1 &
   ```

3. **Запустите Telegram-бота с помощью `nohup`:**
   ```
   cd /path/to/VFS-Global
   nohup python tg-bot.py > bot.log 2>&1 &
   ```

4. **Проверьте, что процессы работают:**
   ```
   ps aux | grep python
   tail -f site/site.log
   tail -f bot.log
   ```

5. **Остановить процесс можно через `kill` по PID:**
   ```
   ps aux | grep python
   kill <PID>
   ```

---

**Примечания:**
- Для автозапуска используйте systemd или supervisor.
- Для публичного доступа к сайту используйте nginx как reverse proxy.