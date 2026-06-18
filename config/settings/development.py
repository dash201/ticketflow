from .base import *

# En dev : tout est permissif
DEBUG = True
ALLOWED_HOSTS = ['*']

# SQLite en dev — zéro config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS ouvert en dev (le frontend tourne sur un autre port)
CORS_ALLOW_ALL_ORIGINS = True

# Ajouter la browsable API en dev
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]