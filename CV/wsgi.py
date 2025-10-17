"""
WSGI config for CV project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV.settings')

application = get_wsgi_application()

# Racine des fichiers statiques (même que dans settings.py)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Ajout de WhiteNoise
application = WhiteNoise(application, root=str(STATIC_ROOT))

