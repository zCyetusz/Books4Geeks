@echo off
REM Installation script for Books4Geeks project (Windows)

echo 📚 Books4Geeks Installation Script
echo ==================================

REM Check Python version
echo 🐍 Checking Python version...
python --version

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install all requirements
echo 📦 Installing all requirements...
pip install -r requirements.txt

REM Django setup
echo 🚀 Setting up Django...

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️ Please edit .env file with your configuration
)

REM Run migrations
echo 🗄️ Running database migrations...
python manage.py migrate

REM Ask for superuser creation
set /p create_superuser="👤 Do you want to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Ask for mock data generation
set /p generate_mock="🎲 Do you want to generate mock data? (y/n): "
if /i "%generate_mock%"=="y" (
    echo 🎲 Generating mock data...
    python manage.py generate_mock_data
)

echo.
echo ✅ Installation completed successfully!
echo.
echo 🚀 To start the development server, run:
echo    python manage.py runserver
echo.
echo 🌐 Then visit http://127.0.0.1:8000/ in your browser
echo.
echo 📖 For more information, see the README.md file
pause
