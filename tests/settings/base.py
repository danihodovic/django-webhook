from pathlib import Path

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "very-secret"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "NAME": "postgres",
        "ATOMIC_REQUESTS": True,
    }
}

ROOT_URLCONF = "tests.urls"

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
]  # type: ignore

LOCAL_APPS = ["django_webhook", "tests"]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

SITE_ID = 1
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(__file__).parent / "media"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True
# CELERY_TASK_STORE_EAGER_RESULT = True
CELERY_BROKER_URL = "redis://redis:6379/"

DJANGO_WEBHOOK = dict(
    MODELS=["tests.Country", "tests.User", "tests.ModelWithFileField"]
)
