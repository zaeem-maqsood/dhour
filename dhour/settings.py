"""
Django settings for dhour project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import requests
from dotenv import load_dotenv, find_dotenv
import logging

# Set up logging
LOGGER = logging.getLogger(__name__)

# Load environment definition file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = BASE_DIR / "templates"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-r(a)4u@#89$^(3k!%8tdtimt-o)*^2(s^pg+q&u=z7_u*f8$3k"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = ("dhour.backend.PermissionBackend",)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "mozilla_django_oidc",
    "corsheaders",
    "rest_framework",
    # Local apps
    "ayats",
    "users",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
]

ROOT_URLCONF = "dhour.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dhour.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "mozilla_django_oidc.contrib.drf.OIDCAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}


CORS_ALLOW_ALL_ORIGINS = False  # Set to False for security reasons
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # The URL of your Nuxt.js frontend
]

# Optionally, you can use CORS_ALLOW_CREDENTIALS to allow cookies to be included in cross-origin requests
CORS_ALLOW_CREDENTIALS = True


def discover_oidc(discovery_url: str) -> dict:
    """
    Performs OpenID Connect discovery to retrieve the provider configuration.
    """
    response = requests.get(discovery_url)
    logging.info(f"OpenID Connect discovery response: {response.json()}")
    if response.status_code != 200:
        raise ValueError("Failed to retrieve provider configuration.")

    provider_config = response.json()

    # Extract endpoint URLs from provider configuration
    return {
        "authorization_endpoint": provider_config["authorization_endpoint"],
        "token_endpoint": provider_config["token_endpoint"],
        "userinfo_endpoint": provider_config["userinfo_endpoint"],
        "jwks_uri": provider_config["jwks_uri"],
    }


# OpenID Connect settings
OIDC_RP_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
OIDC_OP_BASE_URL = os.environ.get("AUTH0_DOMAIN")

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_SCOPES = "openid profile email"
OIDC_OP_DISCOVERY_ENDPOINT = OIDC_OP_BASE_URL + "/.well-known/openid-configuration"

# Discover OpenID Connect endpoints
discovery_info = discover_oidc(OIDC_OP_DISCOVERY_ENDPOINT)
OIDC_OP_AUTHORIZATION_ENDPOINT = discovery_info["authorization_endpoint"]
OIDC_OP_TOKEN_ENDPOINT = discovery_info["token_endpoint"]
OIDC_OP_USER_ENDPOINT = discovery_info["userinfo_endpoint"]
OIDC_OP_JWKS_ENDPOINT = discovery_info["jwks_uri"]

LOGIN_REDIRECT_URL = "http://127.0.0.1:8000/admin"
LOGOUT_REDIRECT_URL = "http://127.0.0.1:8000/admin"
LOGIN_URL = "http://127.0.0.1:8000/oidc/authenticate/"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Set higher level to suppress default Django logging
            "propagate": False,  # Prevent the logs from propagating to the root logger
        },
        "custom_logger": {  # Define your custom logger
            "handlers": ["console"],
            "level": "INFO",  # Set to DEBUG to capture all logs from this logger
            "propagate": False,  # This will prevent the logs from being handled by parent loggers
        },
    },
}


# if DEBUG:
#     # make all loggers use the console.
#     for logger in LOGGING["loggers"]:
#         LOGGING["loggers"][logger]["handlers"] = ["console"]
