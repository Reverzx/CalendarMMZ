
# Quick Start Guide

## Быстрый запуск за 3 шага

### 1. Получите Telegram Bot Token

1. Откройте Telegram
2. Найдите [@BotFather](https://t.me/botfather)
3. Отправьте команду `/newbot`
4. Следуйте инструкциям
5. Скопируйте полученный токен

### 2. Настройте окружение

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

Скрипт автоматически:
- Создаст файл `.env` из шаблона
- Откроет его для редактирования
- Вставьте ваш `TELEGRAM_BOT_TOKEN`
- Запустит Docker контейнеры

### 3. Откройте приложение

Веб-интерфейс: [http://localhost:5000](http://localhost:5000)

## Ручная настройка

Если скрипты не работают:

```bash
# 1. Скопируйте шаблон
cp .env.example .env

# 2. Отредактируйте .env и добавьте токен
nano .env

# 3. Запустите Docker
docker-compose up -d --build

# 4. Проверьте логи
docker-compose logs -f
```

## Первое использование

### Веб-интерфейс
1. Откройте http://localhost:5000
2. Кликните на день в календаре
3. Создайте событие

### Telegram бот
1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Используйте `/addevent` для создания события

## Команды Docker

```bash
# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Полная очистка
docker-compose down -v
```

## Проблемы?

Смотрите полную документацию в [README.md](README.md)
