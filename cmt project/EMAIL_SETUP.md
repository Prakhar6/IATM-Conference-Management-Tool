# 📧 Email Notification System Setup Guide

This guide explains how to set up and use the email notification system for the Conference Management Tool.

## 🚀 Features

The email notification system provides:

1. **Submission Confirmation Emails** - Sent to all authors when a paper is submitted
2. **Review Assignment Emails** - Sent to reviewers when they are assigned to review a paper
3. **Review Notification Emails** - Sent to authors when a review is submitted

## ⚙️ Configuration

### 1. Update Email Settings

Edit `cmt/settings.py` and update the email configuration:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Your email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your email address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Your app password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Your email address
```

### 2. Gmail Setup (Recommended)

If using Gmail:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use the generated password as `EMAIL_HOST_PASSWORD`

### 3. Alternative Email Providers

#### Outlook/Hotmail:
```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### Yahoo:
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### Custom SMTP Server:
```python
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # or False for SSL
```

### 4. Development Testing

For development/testing, you can use the console backend to see emails in the terminal:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## 🧪 Testing

### 1. Test Email Configuration

Run the test script to verify your email setup:

```bash
python test_emails.py
```

### 2. Test in Django Shell

```python
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test Email',
    message='This is a test email.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-email@example.com'],
    fail_silently=False,
)
```

## 📧 Email Templates

The system uses three HTML email templates:

1. **`submissions/emails/submission_confirmation.html`** - Submission confirmation
2. **`submissions/emails/review_notification.html`** - Review received notification
3. **`submissions/emails/reviewer_assignment.html`** - Reviewer assignment notification

### Customizing Templates

You can customize the email templates by editing the HTML files. The templates use:
- Responsive design for mobile and desktop
- Professional styling with your brand colors
- Clear call-to-action buttons
- Comprehensive information display

## 🔧 How It Works

### 1. Submission Confirmation

When a user submits a paper:
- Email is sent to the primary author
- Email is sent to all co-authors (if any)
- Email includes submission details and next steps

### 2. Reviewer Assignment

When a chair assigns reviewers:
- Email is sent to each assigned reviewer
- Email includes submission details and review guidelines
- Direct links to submit review and view submission

### 3. Review Notification

When a reviewer submits a review:
- Email is sent to all authors of the submission
- Email includes review details and recommendations
- Email shows review comments and next steps

## 📋 Email Content

### Submission Confirmation Email
- ✅ Confirmation message
- 📄 Paper details (title, track, date)
- 👥 Author information
- 🔗 Links to view submission and conference
- 📋 Next steps information

### Review Assignment Email
- 📋 Assignment notification
- 📄 Submission details
- 🎯 Review guidelines and criteria
- 🔗 Direct links to submit review
- ⏰ Important deadlines and information

### Review Notification Email
- 📝 Review summary with recommendation
- 👤 Reviewer information
- 💬 Review comments (if provided)
- 🎯 What the recommendation means
- 📋 Next steps for authors

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your email and password
   - Ensure 2FA is enabled and app password is correct
   - Verify SMTP settings for your provider

2. **Connection Refused**
   - Check firewall settings
   - Verify SMTP port (usually 587 or 465)
   - Ensure TLS/SSL settings are correct

3. **Emails Not Sending**
   - Check Django logs for error messages
   - Verify email settings in settings.py
   - Test with console backend first

4. **Emails Going to Spam**
   - Use a professional email address
   - Include proper headers and formatting
   - Consider using a dedicated email service

### Debug Mode

Enable debug logging for emails:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🔒 Security Considerations

1. **Never commit email passwords to version control**
2. **Use environment variables for sensitive data**
3. **Enable 2FA on email accounts**
4. **Use app passwords instead of main passwords**
5. **Regularly rotate app passwords**

### Environment Variables (Recommended)

Create a `.env` file:

```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Update settings.py:

```python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
```

## 📱 Mobile Optimization

All email templates are:
- ✅ Mobile-responsive
- ✅ Cross-platform compatible
- ✅ Accessible design
- ✅ Professional appearance

## 🎨 Customization

### Branding
- Update colors in email templates
- Add your organization's logo
- Customize fonts and styling

### Content
- Modify email text and messaging
- Add additional information sections
- Include custom call-to-action buttons

### Localization
- Support multiple languages
- Add language-specific templates
- Include regional formatting

## 📊 Monitoring

Track email delivery and engagement:
- Monitor email logs
- Check delivery rates
- Track open rates (if using tracking service)
- Monitor bounce rates

## 🚀 Production Deployment

1. **Use production email service** (SendGrid, Mailgun, etc.)
2. **Set up proper DNS records** (SPF, DKIM, DMARC)
3. **Monitor email reputation**
4. **Implement rate limiting**
5. **Set up bounce handling**

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Django email documentation
3. Check your email provider's SMTP documentation
4. Test with console backend first
5. Check Django logs for detailed error messages

---

**Note**: This email system is designed to work with standard SMTP providers. For high-volume production use, consider using dedicated email services like SendGrid, Mailgun, or Amazon SES.
