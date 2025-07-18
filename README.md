# VFS Global Visa Appointment Monitor

Система мониторинга свободных слотов для записи на визу в VFS Global с интеграцией Telegram-бота и веб-дашборда.

## Описание

Проект включает:
- **Telegram Bot** - интерфейс для пользователей
- **Flask Web Dashboard** - веб-дашборд с метриками
- **VFS Parser/Monitor** - автоматический мониторинг слотов
- **Database** - SQLite база данных для хранения данных

## Быстрый старт с Docker

### 1. Подготовка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd VFS-bot-

# Создать файл с переменными окружения
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте файл `.env`:

```env
# VFS Global данные для входа
YOUR_EMAIL=your_email@example.com
PASSWORD=your_password

# Личная информация
FIRST_NAME=Your_First_Name
LAST_NAME=Your_Last_Name
PASSPORT_NUMBER=AB1234567
PASSPORT_YEAR=2020
BIRTH_DAY=01/01/1990
SEX=Male
NATIONALITY=BLR
COUNTRY_CODE=+375
PHONE_NUMBER=291234567

# Настройки визы
CITY=Minsk
VISA_CATEGORY=C
VISA_SUBCATEGORY=C01

# Telegram Bot
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ

# Email уведомления (опционально)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Прокси (опционально)
PROXY_SERVER=http://proxy.example.com:8080
```

### 3. Запуск

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотреть логи
docker-compose logs -f
```

### 4. Доступ к сервисам

- **Веб-дашборд**: http://localhost:5000
- **Telegram Bot**: найдите своего бота в Telegram и отправьте `/start`

## Управление сервисами

```bash
# Остановить все сервисы
docker-compose down

# Перезапустить определенный сервис
docker-compose restart telegram-bot

# Просмотреть логи конкретного сервиса
docker-compose logs -f vfs-monitor

# Пересобрать образы
docker-compose up --build -d
```

## Структура проекта

```
VFS-bot-/
├── docker-compose.yml      # Конфигурация Docker Compose
├── Dockerfile             # Образ для всех сервисов
├── requirements.txt       # Python зависимости
├── .env.example          # Пример переменных окружения
│
├── site/                 # Flask веб-дашборд
│   ├── app.py           # Главный файл приложения
│   └── templates/       # HTML шаблоны
│
├── vfs_parser/          # Модуль мониторинга VFS
│   ├── monitoring.py    # Основной скрипт мониторинга
│   ├── config/          # Конфигурация браузера
│   ├── pages/           # Скрипты для работы со страницами
│   └── utils/           # Утилиты
│
├── tg-bot.py            # Telegram бот
├── auto_booker.py       # Автоматическое бронирование
├── database.py          # Работа с базой данных
└── database.db          # SQLite база данных
```

## Функциональность

### Telegram Bot
- Регистрация пользователей
- Настройка параметров визы
- Запуск/остановка мониторинга
- Уведомления о свободных слотах

### Web Dashboard
- Просмотр метрик в реальном времени
- Мониторинг активных пользователей
- Отслеживание ошибок
- Prometheus метрики

### VFS Monitor
- Автоматическая проверка слотов
- Обход Cloudflare защиты
- Email уведомления
- Логирование ошибок

## Разработка

### Локальная разработка без Docker

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить сервисы отдельно
python site/app.py                    # Веб-дашборд
python tg-bot.py                      # Telegram бот
python vfs_parser/monitoring.py      # VFS мониторинг
```

### Отладка

```bash
# Подключиться к контейнеру
docker-compose exec telegram-bot bash

# Просмотреть логи с фильтрацией
docker-compose logs vfs-monitor | grep ERROR

# Проверить переменные окружения
docker-compose exec telegram-bot printenv | grep BOT_TOKEN
```
