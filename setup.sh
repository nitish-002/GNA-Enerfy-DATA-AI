#!/bin/bash

echo "Setting up GNA Insights Django Application..."

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install build tools first
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip
pip install setuptools wheel

# Install requirements
echo "Installing requirements..."
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1

# Verify Django installation
echo "Verifying Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Run Django setup
echo "Setting up Django..."
python manage.py makemigrations core
python manage.py migrate

# Create superuser (optional - will prompt)
echo "Creating superuser (you can skip this by pressing Ctrl+C)..."
echo "Username: admin"
echo "Email: admin@gna.com"
echo "Password: admin123"
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@gna.com', 'admin123')" | python manage.py shell

# Generate sample data
echo "Generating sample data..."
python manage.py ingest_data --generate-sample --days 30

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start server: python manage.py runserver"
echo "3. Visit: http://127.0.0.1:8000"
echo ""
echo "Admin credentials:"
echo "Username: admin"
echo "Password: admin123"
