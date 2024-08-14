# settings.py

from pathlib import Path
from dotenv import load_dotenv
import os 
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY') 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'main',  # เพิ่ม app ของเรา
    'corsheaders',
    'drf_spectacular',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'msoapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'msoapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',  # สมมติว่าคุณสร้าง folder 'locale' ไว้ใน root directory ของโปรเจค
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # กำหนดตำแหน่งเก็บ static files ใน production

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# rest fram work config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
AUTH_USER_MODEL  = 'main.CustomUser'  # กำหนด custom user model (เราจะสร้างในภายหลัง)
AUTHENTICATION_BACKENDS = [
    'main.backends.CustomAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # ยังคงใช้ ModelBackend เผื่อไว้ในกรณีที่ต้องการ
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000'
  # อนุญาตให้โดเมนนี้ส่ง request มาได้
    # เพิ่มโดเมนอื่นๆ ได้ตามต้องการ
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'MSO Virtual Data API',  # ชื่อของ API ของคุณ
    'DESCRIPTION': 'เอกสารกำกับการใช้ API for MSO data Project',  # คำอธิบาย API
    'VERSION': '1.0.0',  # เวอร์ชันของ API
     'SERVERS': [
    #     {'url': 'https://example.com', 'description': 'Production server'},
         {'url': 'http://127.0.0.1:8000', 'description': 'Local development server'},
     ],  # กำหนด servers หากจำเป็น
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # ปรับเวลาตามความเหมาะสม
    'REFRESH_TOKEN_LIFETIME': timedelta(days=5),     # ปรับเวลาตามความเหมาะสม
    'ROTATE_REFRESH_TOKENS': True,                   # สร้าง refresh token ใหม่ทุกครั้งที่มีการ refresh
    'BLACKLIST_AFTER_ROTATION': True,                # เพิ่ม token เก่าลงใน blacklist หลังจาก rotate
    'UPDATE_LAST_LOGIN': True,                       # อัปเดต last_login ของผู้ใช้ทุกครั้งที่ใช้งาน token
    'ALGORITHM': 'HS256',                             # อัลกอริทึมสำหรับการเข้ารหัส (สามารถเปลี่ยนเป็น RS256 หากต้องการความปลอดภัยสูงขึ้น)
    #'SIGNING_KEY': env('SIGNING_KEY'),                # กุญแจสำหรับการเข้ารหัส (ควรเก็บเป็นความลับ)
    'AUTH_HEADER_TYPES': ('Bearer',),                 # ประเภทของ header สำหรับการส่ง token
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',         # ชื่อของ header สำหรับการส่ง token
    'USER_ID_FIELD': 'id',                            # ฟิลด์ที่ใช้ระบุผู้ใช้ใน token
    'USER_ID_CLAIM': 'user_id',                       # ชื่อของ claim ที่เก็บ ID ของผู้ใช้
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',                 # ชื่อของ claim ที่เก็บประเภทของ token
}