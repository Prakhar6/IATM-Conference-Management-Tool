# 🚀 Production Deployment Guide for IATM Conference Management Tool

This guide will help you properly deploy your Django application on EC2 with working static files and proper styling.

## 🔧 **Current Issues Fixed:**

1. ✅ **Static files not loading** - Added proper STATIC_ROOT and production static file serving
2. ✅ **Django admin styling broken** - Fixed static file configuration
3. ✅ **Navbar styling missing** - Updated templates to use proper static file references
4. ✅ **Production security** - Added security headers and proper DEBUG settings
5. ✅ **Web server configuration** - Added Gunicorn configuration for production

## 📋 **Step-by-Step Deployment:**

### **Step 1: Update Your EC2 Instance**

SSH into your EC2 instance and navigate to your project:

```bash
ssh -i your-key.pem ubuntu@ec2-3-144-197-215.us-east-2.compute.amazonaws.com
cd IATM-Conference-Management-Tool/cmt\ project/
```

### **Step 2: Install Production Dependencies**

```bash
# Activate virtual environment
source ../.venv/bin/activate

# Install production requirements
pip install -r requirements_production.txt
```

### **Step 3: Collect Static Files**

```bash
# This creates the staticfiles/ directory with all your CSS, JS, and images
python manage.py collectstatic --noinput
```

### **Step 4: Set Proper Permissions**

```bash
# Set permissions for static files
chmod -R 755 staticfiles/
chmod -R 755 media/
```

### **Step 5: Test the Application**

```bash
# Test with Gunicorn
gunicorn --config gunicorn_config.py cmt.wsgi:application
```

### **Step 6: Set Up Systemd Service**

```bash
# Copy the service file to systemd
sudo cp iatm-cmt.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable iatm-cmt
sudo systemctl start iatm-cmt

# Check status
sudo systemctl status iatm-cmt
```

### **Step 7: Configure Nginx (Recommended)**

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/iatm-cmt
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name ec2-3-144-197-215.us-east-2.compute.amazonaws.com;

    location /static/ {
        alias /home/ubuntu/IATM-Conference-Management-Tool/cmt project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/ubuntu/IATM-Conference-Management-Tool/cmt project/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/iatm-cmt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔍 **Troubleshooting:**

### **Check Service Status:**
```bash
sudo systemctl status iatm-cmt
sudo journalctl -u iatm-cmt -f
```

### **Check Nginx Status:**
```bash
sudo systemctl status nginx
sudo nginx -t
```

### **Check Static Files:**
```bash
ls -la staticfiles/
ls -la staticfiles/css/
ls -la staticfiles/images/
```

### **Check Logs:**
```bash
tail -f django.log
sudo tail -f /var/log/nginx/error.log
```

## 🌐 **Access Your Site:**

- **Main Site**: http://ec2-3-144-197-215.us-east-2.compute.amazonaws.com/
- **Admin**: http://ec2-3-144-197-215.us-east-2.compute.amazonaws.com/admin/
- **Login**: http://ec2-3-144-197-215.us-east-2.compute.amazonaws.com/accounts/login/

## 🔒 **Security Considerations:**

1. **Update SECRET_KEY** - Generate a new secret key for production
2. **HTTPS** - Consider adding SSL certificate for production
3. **Firewall** - Ensure only necessary ports are open
4. **Database** - Use environment variables for database credentials

## 📝 **Environment Variables (Recommended):**

Create a `.env` file:

```bash
SECRET_KEY=your-new-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## 🚀 **Quick Deployment Commands:**

```bash
# One-command deployment
cd /home/ubuntu/IATM-Conference-Management-Tool/cmt\ project/
source ../.venv/bin/activate
pip install -r requirements_production.txt
python manage.py collectstatic --noinput
chmod -R 755 staticfiles/ media/
sudo systemctl restart iatm-cmt
sudo systemctl restart nginx
```

## ✅ **Verification Checklist:**

- [ ] Static files are collected in `staticfiles/` directory
- [ ] Django admin page loads with proper styling
- [ ] Your custom CSS is loading
- [ ] Images and logos are displaying
- [ ] Service is running without errors
- [ ] Nginx is serving static files
- [ ] Site is accessible from external IP

## 🆘 **Need Help?**

If you encounter issues:

1. Check the service status: `sudo systemctl status iatm-cmt`
2. Check the logs: `sudo journalctl -u iatm-cmt -f`
3. Verify static files: `ls -la staticfiles/`
4. Test static file serving: Visit a CSS file directly in browser

---

**After following this guide, your Django admin and navbar should have proper styling!** 🎉
