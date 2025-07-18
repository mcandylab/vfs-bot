# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Applications

**Flask Web Dashboard:**
```bash
# Activate virtual environment first
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run Flask app
cd site
python app.py
```
Access at: http://127.0.0.1:5000/dashboard

**Telegram Bot:**
```bash
# Set BOT_TOKEN in tg-bot.py first
python tg-bot.py
```

**VFS Parser/Monitoring:**
```bash
# Run from vfs_parser directory
cd vfs_parser
python monitoring.py
```

### Production Deployment (Linux)
```bash
# Run in background with nohup
nohup python site/app.py > site.log 2>&1 &
nohup python tg-bot.py > bot.log 2>&1 &

# Check processes
ps aux | grep python
tail -f site.log
tail -f bot.log
```

## Architecture Overview

This is a **VFS Global visa appointment monitoring system** with three main components:

### 1. Telegram Bot (`tg-bot.py`)
- **Purpose**: User interface for visa appointment monitoring
- **Key Features**: 
  - User registration with visa details (passport, category, city)
  - Start/stop monitoring controls
  - Supports multiple visa categories (C-short term, D-long term)
  - State management with FSM (aiogram)
- **Database**: SQLite (`database.db`) for user data and metrics

### 2. Flask Web Dashboard (`site/app.py`)
- **Purpose**: Real-time monitoring dashboard with metrics
- **Features**:
  - Live metrics display (slots checked, active users, bookings, errors)
  - Prometheus metrics integration
  - Error tracking and logging
- **Templates**: `site/templates/dashboard.html`

### 3. VFS Parser/Monitor (`vfs_parser/`)
- **Purpose**: Core automation engine for checking visa appointments
- **Key Components**:
  - `monitoring.py`: Main monitoring loop
  - `pages/login.py`: VFS Global authentication
  - `pages/check_dates*.py`: Date availability checking
  - `pages/fill_form.py`: Form automation
  - `config/page/page.py`: Browser setup with DrissionPage
  - `utils/email/`: Email notifications
  - `utils/check_elements/`: Cloudflare bypass and loader detection

### 4. Auto Booker (`auto_booker.py`)
- **Purpose**: Slot booking automation
- **Features**: Login, date checking, and slot booking

## Key Technical Details

### Database Schema
- **users**: User registration data (passport, visa category, monitoring status)
- **metrics**: System performance metrics (slots checked, errors, bookings)
- **monitoring_history**: Historical monitoring data

### Browser Automation
- **Engine**: DrissionPage (Chrome/Edge automation)
- **Target**: https://visa.vfsglobal.com/blr/ru/pol
- **Features**: 
  - Anti-detection measures (user agents, headless mode)
  - Cloudflare bypass utilities
  - Proxy support via environment variables

### Configuration
- **Environment Variables**: Set in `vfs_parser/config/.env`
  - Email credentials (SMTP_SERVER, SMTP_USERNAME, etc.)
  - PROXY_SERVER (optional)
  - VFS login credentials
- **Cities**: Configured via environment variable `city`

### Dependencies
- **Core**: aiogram, flask, DrissionPage, sqlite3
- **Utilities**: python-dotenv, prometheus_flask_exporter
- **Authentication**: google-auth libraries
- **Web**: requests

## Development Notes

### Testing
- No formal test framework detected
- Test by running individual components
- Monitor logs: `error.log` in vfs_parser directory

### Logging
- Flask app: Built-in logging with error handlers
- VFS Parser: File logging to `vfs_parser/error.log`
- Database: Error metrics tracked in `metrics` table

### Security Considerations
- Bot token exposed in code (should use environment variables)
- Hardcoded browser paths in `page.py`
- Email credentials via environment variables (good practice)

### File Structure
- `site/`: Flask web application
- `vfs_parser/`: Core monitoring and automation
- `tmp/`: Temporary files (screenshots, etc.)
- Root level: Main entry points and database