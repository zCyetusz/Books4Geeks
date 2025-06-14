#!/bin/bash
# Installation script for Books4Geeks project

echo "📚 Books4Geeks Installation Script"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "🐍 Checking Python version..."
python --version

# Check if pip is installed
if ! command_exists pip; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install all requirements
echo "📦 Installing all requirements..."
pip install -r requirements.txt

# Django setup
echo "🚀 Setting up Django..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your configuration"
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser
read -p "👤 Do you want to create a superuser? (y/n): " create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Generate mock data
read -p "🎲 Do you want to generate mock data? (y/n): " generate_mock
if [[ $generate_mock =~ ^[Yy]$ ]]; then
    echo "🎲 Generating mock data..."
    python manage.py generate_mock_data
fi

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To start the development server, run:"
echo "   python manage.py runserver"
echo ""
echo "🌐 Then visit http://127.0.0.1:8000/ in your browser"
echo ""
echo "📖 For more information, see the README.md file"
