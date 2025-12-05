@echo off
echo Starting Calendar Application...
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your TELEGRAM_BOT_TOKEN!
    echo Press any key to open .env file...
    pause >nul
    notepad .env
)

echo Building and starting Docker containers...
docker-compose up -d --build

if %errorlevel% equ 0 (
    echo.
    echo =========================================
    echo Calendar Application started successfully!
    echo =========================================
    echo.
    echo Web interface: http://localhost:5000
    echo.
    echo To view logs:
    echo   docker-compose logs -f
    echo.
    echo To stop:
    echo   docker-compose down
    echo.
) else (
    echo.
    echo ERROR: Failed to start containers!
    echo Please check Docker is running and try again.
)

pause
