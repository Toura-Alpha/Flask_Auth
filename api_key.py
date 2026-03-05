import os

# Google OAuth credentials - load from environment variables
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# Check if credentials are properly configured
if not CLIENT_ID or not CLIENT_SECRET:
    print("WARNING: Google OAuth credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
