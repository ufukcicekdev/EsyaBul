from esyabul.settings.base import * 
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG=True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DEV_DATABASE_ENGINE'),
        'NAME': os.getenv('DEV_DATABASE_NAME'),
        'USER': os.getenv('DEV_DATABASE_USER'),
        'PASSWORD': os.getenv('DEV_DATABASE_PASSWORD'),
        'HOST': os.getenv('DEV_DATABASE_HOST'),
        'PORT': os.getenv('DEV_DATABASE_PORT'),
        'OPTIONS': {
            'sslmode': 'require',  # SSL gereklilik durumu
        },
    }
}


AWS_ACCESS_KEY_ID = os.getenv('DEV_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('DEV_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('DEV_AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = os.getenv('DEV_AWS_S3_CUSTOM_DOMAIN')
AWS_DEFAULT_ACL = os.getenv('DEV_AWS_DEFAULT_ACL')
AWS_S3_REGION_NAME = os.getenv("DEV_AWS_S3_REGION_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("DEV_AWS_S3_ENDPOINT_URL")
AWS_LOCATION = os.getenv("DEV_AWS_LOCATION")
DEFAULT_FILE_STORAGE = 'esyabul.storage_backends.CustomS3Boto3Storage'