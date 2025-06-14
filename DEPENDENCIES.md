# 📦 Dependencies Guide

## Overview

The Books4Geeks project uses a comprehensive single requirements.txt file that contains all necessary dependencies for development, production, and AI features.

- **`requirements.txt`** - All dependencies (core, development, AI/ML, testing, etc.)

## Installation Methods

### 🚀 Quick Install (Recommended)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### 📦 Manual Installation

**All Dependencies:**
```bash
pip install -r requirements.txt
```

## Dependencies Included

### 🌐 **Web Framework & Production**
- Django 4.2.8 - Main web framework
- django-admin-adminlte - Enhanced admin interface  
- gunicorn - Production WSGI server
- whitenoise - Static file serving
- django-cors-headers - CORS support

### 🗄️ **Database & Storage**
- mysqlclient - MySQL database adapter
- django-extensions - Database utilities
- django-storages - File storage backends
- redis - Caching and session storage

### 🖼️ **Image Processing & AI**
- Pillow - Image manipulation
- opencv-python - Computer vision
- numpy - Numerical computing
- google-generativeai - Gemini AI integration
- tensorflow - Machine learning framework
- scikit-learn - ML algorithms
- scikit-image - Advanced image processing

### 📊 **Data Processing & Analysis**
- pandas - Data analysis
- openpyxl, xlsxwriter - Excel file handling
- reportlab - PDF generation
- matplotlib, seaborn - Data visualization

### 🧪 **Testing & Quality**
- pytest, pytest-django - Testing frameworks
- factory-boy - Test data generation
- flake8, black, isort - Code quality tools
- django-debug-toolbar - Development debugging

### 🎲 **Mock Data & Development**
- Faker - Realistic fake data generation
- django-seed - Database seeding
- django-import-export - Data import/export

### 🔧 **Development & Admin Tools**
- django-crispy-forms - Form rendering
- django-filter - Advanced filtering
- django-ckeditor - Rich text editor
- drf-spectacular - API documentation

### 🚀 **Optional Features**
- celery - Task queue system
- channels - WebSocket support
- django-allauth - Social authentication
- easy-thumbnails - Image thumbnails

All dependencies are included in the single `requirements.txt` file for easy installation.

## Troubleshooting

### Common Issues

**1. EasyOCR Installation Issues (Windows):**
```
Solution: The system has graceful fallbacks. EasyOCR is optional.
Alternative: Use Google Gemini AI (superior performance)
```

**2. OpenCV Installation Issues:**
```bash
# Try alternative installation
pip install opencv-python-headless
```

**3. MySQL Client Issues:**
```bash
# Windows alternative
pip install PyMySQL
```

**4. TensorFlow GPU Issues:**
```bash
# CPU-only version (recommended for most users)
pip install tensorflow-cpu
```

### Version Compatibility

- **Python**: 3.8+ required, 3.12+ recommended
- **Django**: 4.2.x LTS version
- **Node.js**: Not required (pure Python/Django project)

## Environment Configuration

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Edit .env file with your settings:**
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:pass@localhost/books4geeks
GEMINI_API_KEY=your-gemini-api-key
```

## Production Deployment

For production, only install core requirements:
```bash
pip install -r requirements.txt
```

Additional production considerations:
- Use `gunicorn` for WSGI server
- Configure `whitenoise` for static files
- Set `DEBUG=False` in production
- Use environment variables for sensitive data

## Performance Optimization

### Memory Usage
- Core installation: ~500MB
- With AI dependencies: ~2-3GB
- GPU support adds: ~5-10GB

### Installation Time
- Core dependencies: 2-5 minutes
- AI dependencies: 10-20 minutes
- Full installation: 15-30 minutes

## Support

If you encounter dependency issues:

1. Check Python version compatibility
2. Update pip: `pip install --upgrade pip`
3. Use virtual environment: `python -m venv venv`
4. Check system requirements for specific packages
5. Consult package-specific documentation

## License Compliance

All dependencies are compatible with the project's open-source license. Key licenses:
- Django: BSD-3-Clause
- OpenCV: Apache-2.0
- TensorFlow: Apache-2.0
- Pillow: PIL Software License
