@echo off
REM ============================================================================
REM LUMRA DJANGO - SETUP SCRIPT (WINDOWS)
REM ============================================================================
REM Script ini akan setup complete development environment untuk Lumra
REM Usage: setup_lumra.bat
REM ============================================================================

setlocal enabledelayedexpansion
color 0F

echo.
echo ============================================================================
echo LUMRA DJANGO - DEVELOPMENT SETUP (WINDOWS)
echo ============================================================================
echo.

REM ============ Check Prerequisites ============
echo [INFO] Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is required but not installed.
    echo Please download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do (
    echo [OK] %%i found
)

where pip >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip is required but not installed.
    pause
    exit /b 1
)

echo [OK] pip found
echo.

REM ============ Setup Python Virtual Environment ============
echo [INFO] Setting up Python virtual environment...

if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [WARN] Virtual environment already exists, skipping creation
)

call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM ============ Upgrade pip ============
echo [INFO] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo [OK] pip, setuptools, and wheel upgraded
echo.

REM ============ Install Dependencies ============
echo [INFO] Installing Python dependencies from requirements.txt...

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

pip install -r requirements.txt
echo [OK] All dependencies installed
echo.

REM ============ Create .env File ============
echo [INFO] Setting up environment variables...

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] .env file created from .env.example
        echo [WARN] Please update .env file with your configuration
    ) else (
        echo [ERROR] .env.example not found!
        pause
        exit /b 1
    )
) else (
    echo [WARN] .env file already exists, skipping
)
echo.

REM ============ Create Required Directories ============
echo [INFO] Creating required directories...

if not exist "logs" mkdir logs
if not exist "lumra_config\static\css" mkdir lumra_config\static\css
if not exist "lumra_config\static\js" mkdir lumra_config\static\js
if not exist "lumra_config\static\images" mkdir lumra_config\static\images
if not exist "lumra_config\templates" mkdir lumra_config\templates
if not exist "media" mkdir media
if not exist "db_init" mkdir db_init

echo [OK] Directories created
echo.

REM ============ Django Setup ============
echo [INFO] Setting up Django...

if not exist "lumra_system\settings.py" (
    if exist "settings_production.py" (
        copy settings_production.py lumra_system\settings.py
        echo [WARN] settings.py created from settings_production.py
        echo [WARN] Update DATABASE config in settings.py if needed!
    ) else (
        echo [ERROR] settings_production.py not found!
        pause
        exit /b 1
    )
) else (
    echo [WARN] settings.py already exists, skipping
)
echo.

echo [INFO] Running Django migrations...
python manage.py makemigrations
python manage.py migrate
echo [OK] Migrations completed
echo.

echo [INFO] Collecting static files...
python manage.py collectstatic --noinput
echo [OK] Static files collected
echo.

REM ============ Install Pre-commit Hooks ============
echo [INFO] Setting up pre-commit hooks...

if exist ".pre-commit-config.yaml" (
    pip install pre-commit >nul 2>&1
    pre-commit install
    echo [OK] Pre-commit hooks installed
) else (
    echo [WARN] .pre-commit-config.yaml not found, skipping pre-commit setup
)
echo.

REM ============ Create Superuser ============
echo [INFO] Creating superuser...
echo.

set /p create_su="Do you want to create a superuser? (y/n): "

if /i "%create_su%"=="y" (
    python manage.py createsuperuser
    echo [OK] Superuser created
) else (
    echo [WARN] Skipping superuser creation
)
echo.

REM ============ External Services Check ============
echo [INFO] Checking external services...
echo.

where psql >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] PostgreSQL found
) else (
    echo [WARN] PostgreSQL not installed
    echo Please download from: https://www.postgresql.org/download/windows/
)

where redis-cli >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis found
) else (
    echo [WARN] Redis not installed
    echo Download from: https://github.com/microsoftarchive/redis/releases
)
echo.

REM ============ Summary ============
echo ============================================================================
echo [OK] Setup completed successfully!
echo ============================================================================
echo.
echo Next steps:
echo 1. Update .env file with your configuration
echo 2. Start external services:
echo    - Start PostgreSQL (Windows Services or manually)
echo    - Start Redis: redis-server.exe (from Command Prompt)
echo 3. Run development server in Terminal 1:
echo    python manage.py runserver
echo 4. Run Celery Worker in Terminal 2:
echo    celery -A lumra_system worker -l info
echo 5. Run Celery Beat in Terminal 3 (optional):
echo    celery -A lumra_system beat -l info
echo 6. Access admin at: http://localhost:8000/admin
echo.
echo Documentation: LUMRA_UPGRADE_GUIDE.md
echo.

pause
