from esyabul.settings.base import * 
import os
from dotenv import load_dotenv
load_dotenv()

ALLOWED_HOSTS = ["esyala.com","www.esyala.com","web-production-8e47.up.railway.app"]
CSRF_TRUSTED_ORIGINS = ["https://*."]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True




DATABASES = {
    'default': {
        'ENGINE': os.getenv('PROD_DATABASE_ENGINE'),
        'NAME': os.getenv('PROD_DATABASE_NAME'),
        'USER': os.getenv('PROD_DATABASE_USER'),
        'PASSWORD': os.getenv('PROD_DATABASE_PASSWORD'),
        'HOST': os.getenv('PROD_DATABASE_HOST'),
        'PORT': os.getenv('PROD_DATABASE_PORT'),
        'OPTIONS': {
            'sslmode': 'require',  # SSL gereklilik durumu
        },
    }
}


AWS_ACCESS_KEY_ID = os.getenv('PROD_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('PROD_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('PROD_AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = os.getenv('PROD_AWS_S3_CUSTOM_DOMAIN')
AWS_DEFAULT_ACL = os.getenv('PROD_AWS_DEFAULT_ACL')
AWS_S3_REGION_NAME = os.getenv("PROD_AWS_S3_REGION_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("PROD_AWS_S3_ENDPOINT_URL")
AWS_LOCATION = os.getenv("PROD_AWS_LOCATION")
DEFAULT_FILE_STORAGE = 'esyabul.storage_backends.CustomS3Boto3Storage'