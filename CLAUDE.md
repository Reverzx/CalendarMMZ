# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Calendar application with dual interfaces: a Flask web application and a Telegram bot, both sharing a PostgreSQL database. The application runs in three separate Docker containers that communicate via a shared network.

## Architecture

### Three-Service Architecture
- **web** (Flask): Serves HTML calendar UI and REST API endpoints
- **bot** (python-telegram-bot): Async Telegram bot with conversation handlers
- **db** (PostgreSQL): Shared database for both services

Both web and bot services create their own Flask app instance using the factory pattern in `app/__init__.py`. Database migrations happen automatically via `db.create_all()` in the factory function.

### Key Architectural Patterns

**Application Factory**: `app/__init__.py` uses `create_app()` pattern
- Web service: imports in `run.py`
- Bot service: creates app instance in `TelegramBot.__init__()` to access database within Flask context

**Database Access Pattern**:
- Web routes access db directly (already in Flask context)
- Bot handlers must wrap db operations with `with self.app.app_context():`

**Data Sharing**: Events created in web UI are visible to Telegram bot users and vice versa via shared `events` table. Telegram users tracked separately in `telegram_users` table.

## Development Commands

### Docker Operations (Primary Development Method)

```bash
# Start all services (includes automatic database migration)
docker-compose up -d --build

# View logs
docker-compose logs -f          # all services
docker-compose logs -f web      # web application only
docker-compose logs -f bot      # telegram bot only
docker-compose logs -f db       # database only

# Restart services (e.g., after code changes in non-mounted files)
docker-compose restart

# Stop services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Local Development (Without Docker)

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Run web application (terminal 1)
python run.py

# Run telegram bot (terminal 2)
python bot.py
```

**Database Setup for Local Development**: Must create PostgreSQL database manually:
```sql
CREATE DATABASE calendar_db;
CREATE USER calendar_user WITH PASSWORD 'calendar_pass';
GRANT ALL PRIVILEGES ON DATABASE calendar_db TO calendar_user;
```

### Quick Start Scripts

```bash
start.bat    # Windows - interactive setup with .env creation
start.sh     # Linux/Mac - interactive setup with .env creation
```

## Configuration

### Environment Variables
All configuration via `.env` file (copy from `.env.example`):
- `TELEGRAM_BOT_TOKEN`: Required for bot functionality (get from @BotFather)
- `SECRET_KEY`: Flask secret (change for production)
- `DATABASE_URL`: PostgreSQL connection string
- `WEBHOOK_URL`: Currently unused (polling mode)

Configuration loaded via `config.py` using python-dotenv.

## API Endpoints

### REST API (app/routes.py)
- `GET /api/events` - List events (optional query params: `start`, `end` in ISO format)
- `POST /api/events` - Create event (JSON body: title, description, start_time, end_time)
- `PUT /api/events/<id>` - Update event
- `DELETE /api/events/<id>` - Delete event
- `GET /health` - Health check

All endpoints return JSON. Events use ISO 8601 datetime format.

### Telegram Bot Commands (app/telegram_bot.py)
- `/start` - Register user and show welcome
- `/addevent` - Start conversation flow to create event (uses ConversationHandler)
- `/myevents` - List all user's events
- `/today` - Events for current day
- `/tomorrow` - Events for next day
- `/week` - Events for next 7 days
- `/cancel` - Cancel current conversation

Date format for bot: `ДД.ММ.ГГГГ ЧЧ:ММ` (e.g., 25.12.2024 15:30)

## Database Models (app/models.py)

**Event**: Core event model
- `telegram_user_id`: String field (not FK) - stores Telegram user ID if created via bot
- `start_time`, `end_time`: DateTime fields (no timezone awareness)
- `to_dict()`: Serialization method for API responses

**TelegramUser**: Tracks Telegram bot users
- `telegram_id`: Unique Telegram user identifier (string)
- No relationship to Event model (loose coupling by telegram_user_id string matching)

## Frontend (static/)

Vanilla JavaScript calendar implementation:
- `static/js/calendar.js`: Calendar rendering, event CRUD via fetch API
- `static/css/style.css`: Gradient purple theme, modal styling
- `app/templates/calendar.html`: Single-page application

Calendar displays current month, highlights today, shows event indicators. Click day to create event. Modal form for create/edit operations.

## Bot Conversation Flow

`/addevent` uses ConversationHandler with states: TITLE → DESCRIPTION → START_TIME → END_TIME

Each state expects specific text input:
- DESCRIPTION: accepts "пропустить" to skip
- START_TIME, END_TIME: validates datetime format and ensures end > start

Bot stores event with user's `telegram_id` for future filtering.

## Testing Workflow

No test suite currently exists. Manual testing workflow:

1. Start services: `docker-compose up -d`
2. Check web UI: http://localhost:5000
3. Check bot: message your Telegram bot `/start`
4. Create event in web UI, verify visible in bot via `/myevents`
5. Create event via bot `/addevent`, verify visible in web UI
6. View logs: `docker-compose logs -f`

## Common Issues

**Bot not responding**: Verify `TELEGRAM_BOT_TOKEN` in `.env`, check logs: `docker-compose logs -f bot`

**Database connection errors**: Ensure db container is healthy before web/bot start (docker-compose handles via healthcheck + depends_on)

**Port 5000 already in use**: Change port mapping in docker-compose.yml under web service

**Timezone handling**: Application uses `datetime.utcnow()` but no timezone conversion - timestamps stored as naive datetime

## Code Modification Guidelines

**Adding new bot commands**:
1. Create async handler method in `TelegramBot` class
2. Register handler in `run()` method via `application.add_handler()`
3. Access database within `with self.app.app_context():` block

**Adding new API endpoints**:
1. Add route function to `app/routes.py` with `@bp.route()` decorator
2. Use existing `db` import for database operations
3. Return JSON via `jsonify()`

**Database schema changes**:
1. Modify models in `app/models.py`
2. Restart containers (migrations run automatically on startup via `db.create_all()`)
3. For production: consider using Flask-Migrate/Alembic for proper migrations

**Frontend changes**:
- Static files mounted as volumes in docker-compose - changes reflect immediately
- No build step required (vanilla JS/CSS)
