#!/bin/bash

# Production Deployment Script for IATM Conference Management Tool
# Run this script on your EC2 instance to properly deploy Django

echo "🚀 Starting Production Deployment..."

# 1. Navigate to project directory
cd /path/to/your/project  # Update this path

# 2. Activate virtual environment (if using one)
# source venv/bin/activate

# 3. Install/update requirements
echo "📦 Installing/updating requirements..."
pip install -r requirements.txt

# 4. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# 5. Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# 6. Create superuser if needed (uncomment if needed)
# echo "👤 Creating superuser..."
# python manage.py createsuperuser

# 7. Set proper permissions
echo "🔐 Setting proper permissions..."
chmod -R 755 staticfiles/
chmod -R 755 media/

# 8. Restart your web server (update based on your setup)
echo "🔄 Restarting web server..."

# For Gunicorn:
# sudo systemctl restart gunicorn

# For uWSGI:
# sudo systemctl restart uwsgi

# For Apache:
# sudo systemctl restart apache2

# For Nginx:
# sudo systemctl restart nginx

echo "✅ Production deployment completed!"
echo "🌐 Your site should now be accessible with proper styling!"
echo "📝 Check the logs if you encounter any issues:"
echo "   - Django logs: tail -f django.log"
echo "   - Web server logs: check your web server configuration"
