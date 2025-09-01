import os
from paypal_checkout_sdk.client import PayPalClient
from paypal_checkout_sdk.enums import Environment

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', 'your_client_id_here')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', 'your_client_secret_here')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'

def get_paypal_client():
    """Get PayPal client based on environment configuration"""
    if PAYPAL_MODE == 'live':
        environment = Environment.LIVE
    else:
        environment = Environment.SANDBOX
    
    return PayPalClient(
        client_id=PAYPAL_CLIENT_ID,
        client_secret=PAYPAL_CLIENT_SECRET,
        environment=environment
    )

# PayPal URLs
if PAYPAL_MODE == 'live':
    PAYPAL_BASE_URL = 'https://www.paypal.com'
else:
    PAYPAL_BASE_URL = 'https://www.sandbox.paypal.com'
