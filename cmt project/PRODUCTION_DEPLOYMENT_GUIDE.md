# Production Deployment Guide for IATM Conference Management Tool

## 🚀 **Pre-Deployment Checklist**

### ✅ **Code Security Review Completed**
- [x] Database credentials moved to environment variables
- [x] Production security settings enabled
- [x] Debug mode configurable via environment
- [x] PayPal debug prints removed
- [x] SSL/HTTPS security headers configured

### ✅ **Environment Variables Required**
Create a `.env` file in your production server with:

```env
# Django Configuration
SECRET_KEY=your_very_long_random_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip.compute.amazonaws.com

# Database Configuration
DB_NAME=iatm_conference_db
DB_USER=iatm_user
DB_PASSWORD=your_secure_database_password_here
DB_HOST=localhost
DB_PORT=5432

# PayPal Configuration (Production)
PAYPAL_CLIENT_ID=your_live_paypal_client_id
PAYPAL_CLIENT_SECRET=your_live_paypal_client_secret
PAYPAL_MODE=live
```

## 🗄️ **Database Setup**

### **1. PostgreSQL Installation**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### **2. Database Creation**
```bash
sudo -u postgres psql
CREATE DATABASE iatm_conference_db;
CREATE USER iatm_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE iatm_conference_db TO iatm_user;
\q
```

### **3. Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🌐 **Web Server Setup**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Static Files Collection**
```bash
python manage.py collectstatic
```

### **3. Gunicorn Configuration**
```bash
gunicorn --bind 0.0.0.0:8000 cmt.wsgi:application
```

### **4. Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/your/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 **Security Checklist**

### **Firewall Configuration**
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### **SSL Certificate (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📝 **GitHub Deployment Workflow**

### **1. Update .gitignore**
Ensure these files are ignored:
```
.env
*.pyc
__pycache__/
db.sqlite3
media/
staticfiles/
```

### **2. Commit and Push**
```bash
git add .
git commit -m "Production ready: Security fixes and PayPal integration"
git push origin main
```

### **3. Server Pull and Restart**
```bash
# Navigate to the main repository directory
cd ~/IATM-Conference-Management-Tool

# Pull latest changes
git pull origin main

# Navigate to the cmt project subdirectory
cd "cmt project"

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Restart the application
sudo systemctl restart iatm-cmt
```

## 🚨 **Critical Security Notes**

1. **NEVER commit .env files** to GitHub
2. **Use strong, unique passwords** for database and admin
3. **Enable HTTPS** before going live
4. **Regular security updates** for OS and packages
5. **Monitor logs** for suspicious activity
6. **Backup database** regularly

## 🔧 **Troubleshooting**

### **Common Issues:**
- **500 errors**: Check DEBUG=False and environment variables
- **Database connection**: Verify PostgreSQL is running and credentials
- **Static files**: Run `collectstatic` and check nginx paths
- **PayPal errors**: Verify live credentials and mode

### **Logs to Check:**
- Django logs: `tail -f django.log`
- Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- System logs: `sudo journalctl -u your-app-service`

## 📞 **Next Steps**

1. **Set up your EC2 instance**
2. **Install PostgreSQL and dependencies**
3. **Configure environment variables**
4. **Set up nginx and gunicorn**
5. **Test PayPal integration**
6. **Go live!**

Need help with EC2 setup? Let me know!
