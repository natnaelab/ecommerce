from .base import *

SECRET_KEY = "django-insecure-2i^i*ho*@e%z4sjze61^c)u^-s$23)q0(42-zv_%epe9&ar*$z"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

INTERNAL_IPS = ["127.0.0.1"]
DEBUG_TOOLBAR_PANELS = ["debug_toolbar.panels.sql.SQLPanel"]
RESULTS_CACHE_SIZE = 5
ENABLE_STACKTRACES = True
