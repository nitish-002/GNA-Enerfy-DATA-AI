#!/bin/bash

echo "Manual Setup for GNA Insights Django Application..."

# Remove existing venv
rm -rf venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages one by one
echo "Installing Django..."
pip install Django==4.2.7

echo "Installing Django REST Framework..."
pip install djangorestframework==3.14.0

echo "Installing Django CORS Headers..."
pip install django-cors-headers==4.3.1

echo "Creating necessary directories..."
mkdir -p core/management/commands
mkdir -p templates/core
mkdir -p static

# Create __init__.py files
touch core/__init__.py
touch core/management/__init__.py
touch core/management/commands/__init__.py
touch gna_insights/__init__.py

echo "Django setup..."
python manage.py makemigrations core
python manage.py migrate

echo "Creating superuser..."
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@gna.com', 'admin123')" | python manage.py shell

echo "Generating sample data..."
python manage.py ingest_data --generate-sample --days 30

echo "Setup complete!"
