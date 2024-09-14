import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from pathlib import Path

# Replace with your Firebase project's credentials
# if(os.environ.get('SETTINGS')=='prod'):
#     cred = credentials.Certificate({
#         "type": os.getenv('FIREBASE_TYPE'),
#         "project_id": os.getenv('FIREBASE_PROJECT_ID'),
#         "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
#         "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
#         "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
#         "client_id": os.getenv('FIREBASE_CLIENT_ID'),
#         "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
#         "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
#         "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL'),
#         "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL'),
#         "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN')
#     })
# else:
#     cred = credentials.Certificate({
#         "type": os.getenv('DEV_FIREBASE_TYPE'),
#         "project_id": os.getenv('DEV_FIREBASE_PROJECT_ID'),
#         "private_key_id": os.getenv('DEV_FIREBASE_PRIVATE_KEY_ID'),
#         "private_key": os.getenv('DEV_FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
#         "client_email": os.getenv('DEV_FIREBASE_CLIENT_EMAIL'),
#         "client_id": os.getenv('DEV_FIREBASE_CLIENT_ID'),
#         "auth_uri": os.getenv('DEV_FIREBASE_AUTH_URI'),
#         "token_uri": os.getenv('DEV_FIREBASE_TOKEN_URI'),
#         "auth_provider_x509_cert_url": os.getenv('DEV_FIREBASE_AUTH_PROVIDER_CERT_URL'),
#         "client_x509_cert_url": os.getenv('DEV_FIREBASE_CLIENT_CERT_URL'),
#         "universe_domain": os.getenv('DEV_FIREBASE_UNIVERSE_DOMAIN')
#     })
# firebase_admin.initialize_app(cred)
