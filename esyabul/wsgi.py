"""
WSGI config for esyabul project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from esyabul.settings import base

if base.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "esyabul.settings.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "esyabul.settings.production")


application = get_wsgi_application()
