#!/bin/bash

echo "Installing GNA Insights dependencies..."

# Remove existing venv if it has issues
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install setuptools and wheel first
echo "Installing build tools..."
pip install setuptools>=65.0.0 wheel

# Install Django packages one by one
echo "Installing Django..."
pip install Django==4.2.7

echo "Installing Django REST Framework..."
pip install djangorestframework==3.14.0

echo "Installing Django CORS Headers..."
pip install django-cors-headers==4.3.1

echo "Creating Django project structure..."

# Create gna_insights directory and __init__.py
mkdir -p gna_insights
touch gna_insights/__init__.py

# Create core app directories
mkdir -p core/management/commands
mkdir -p core/sample_data
mkdir -p templates/core
mkdir -p static

# Create all necessary __init__.py files
touch core/__init__.py
touch core/management/__init__.py
touch core/management/commands/__init__.py

echo "Django project structure created successfully!"

echo "Installation complete!"
echo ""
echo "To activate the virtual environment:"
echo "source venv/bin/activate"
echo ""
echo "To run Django setup:"
echo "python manage.py makemigrations core"
echo "python manage.py migrate"
echo "python manage.py runserver"
echo ""
echo "Next steps:"
echo "1. Run: source venv/bin/activate"
echo "2. Run: python manage.py makemigrations core"
echo "3. Run: python manage.py migrate"
echo "4. Run: python manage.py createsuperuser"
echo "5. Run: python manage.py ingest_data --generate-sample --days 30"
echo "6. Run: python manage.py runserver"
