# 🚀 PayPal Integration Setup Guide

This guide will help you set up PayPal payments for the IATM Conference Management Tool.

## 📋 Prerequisites

1. **PayPal Developer Account**: Sign up at [developer.paypal.com](https://developer.paypal.com/)
2. **Python Environment**: Make sure you have Python 3.8+ installed
3. **Django Project**: This should already be set up

## 🔑 Step 1: Get PayPal Credentials

### 1.1 Create PayPal App
1. Go to [developer.paypal.com](https://developer.paypal.com/)
2. Log in with your PayPal account
3. Navigate to "My Apps & Credentials"
4. Click "Create App"
5. Give your app a name (e.g., "IATM Conference Tool")
6. Select "Business" account type
7. Click "Create App"

### 1.2 Get Credentials
1. After creating the app, you'll see:
   - **Client ID**: Copy this
   - **Client Secret**: Copy this
2. **Important**: Keep these credentials secure!

## 🛠️ Step 2: Set Up Environment Variables

### Option A: Use the Setup Script (Recommended)
```bash
python setup_paypal.py
```
This script will:
- Ask for your PayPal credentials
- Create a `.env` file automatically
- Set up sandbox/live mode
- Generate a secure Django secret key

### Option B: Manual Setup
1. Create a `.env` file in your project root:
```bash
# PayPal Configuration
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_MODE=sandbox

# Django Configuration
SECRET_KEY=your_generated_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 🧪 Step 3: Test with Sandbox

### 3.1 Sandbox Accounts
PayPal provides test accounts for development:
- **Buyer Account**: `sb-1234567890@business.example.com`
- **Seller Account**: `sb-1234567890@business.example.com`
- **Password**: Check your PayPal developer dashboard

### 3.2 Test Payment Flow
1. Start your Django server: `python manage.py runserver`
2. Go to a conference page
3. Click "Register" button
4. Complete payment with sandbox buyer account
5. Verify payment success

## 🚀 Step 4: Go Live (Production)

### 4.1 Switch to Live Mode
1. Update your `.env` file:
```bash
PAYPAL_MODE=live
```

### 4.2 Update PayPal App
1. Go to PayPal Developer Dashboard
2. Change app from "Sandbox" to "Live"
3. Get new live credentials
4. Update `.env` file with live credentials

### 4.3 Security Checklist
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is secure and unique
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] HTTPS enabled
- [ ] Environment variables are secure

## 🔧 Configuration Details

### PayPal Modes
- **Sandbox**: For testing and development
- **Live**: For real payments in production

### Payment Flow
1. User clicks "Register" button
2. Django creates PayPal order
3. User redirected to PayPal
4. User completes payment
5. PayPal redirects back to success/cancel URL
6. Django verifies payment and updates membership

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `PAYPAL_CLIENT_ID` | Your PayPal app client ID | `AbC123...` |
| `PAYPAL_CLIENT_SECRET` | Your PayPal app client secret | `XyZ789...` |
| `PAYPAL_MODE` | Payment mode | `sandbox` or `live` |

## 🐛 Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
pip install paypal-checkout-sdk python-dotenv
```

#### 2. PayPal redirect errors
- Check return URLs in PayPal app settings
- Verify `ALLOWED_HOSTS` includes your domain
- Ensure HTTPS in production

#### 3. Payment verification fails
- Check PayPal credentials
- Verify sandbox/live mode matches
- Check server logs for errors

#### 4. Session errors
- Ensure `django.contrib.sessions` is in `INSTALLED_APPS`
- Check session middleware configuration

### Debug Mode
For development, you can enable debug:
```bash
DEBUG=True
```

This will show detailed error messages.

## 📚 Additional Resources

- [PayPal Developer Documentation](https://developer.paypal.com/docs/)
- [PayPal Checkout SDK](https://github.com/paypal/Checkout-Python-SDK)
- [Django Environment Variables](https://django-environ.readthedocs.io/)

## 🎯 Next Steps

After setting up PayPal:

1. **Test thoroughly** with sandbox accounts
2. **Customize payment flow** if needed
3. **Add payment logging** for admin tracking
4. **Implement webhooks** for real-time updates
5. **Add payment analytics** and reporting

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Django and PayPal logs
3. Verify environment variable configuration
4. Test with sandbox mode first

---

**Happy coding! 🎉**
