# Django settings for bmc project.

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/mushroomclub/media.bostonmycologicalclub.org'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
#MEDIA_URL = 'http://mediabmc.dreamhosters.com/'
MEDIA_URL = 'http://media.bostonmycologicalclub.org'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = 'http://mediabmc.dreamhosters.com/admin_media/'
ADMIN_MEDIA_PREFIX = 'http://media.bostonmycologicalclub.org/admin_media/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

AUTH_PROFILE_MODULE = 'main.UserProfile'

AUTHENTICATION_BACKENDS = (
    'bmc.main.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)

ROOT_URLCONF = 'bmc.urls'

#SESSION_COOKIE_DOMAIN = ''

import os.path

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 
                 'templates').replace('\\','/'),
#    '/home/petevg/html/bmc/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'bmc.main',
)

# Date/Time Settings
TIME_FORMAT='g:i A'
#DATE_FORMAT = 'm/d/Y'

# BMC Specific Config
#USER_TYPES = (
#    ('member', 'Member'),
#    ('walk_moderator', 'Walk Moderator'),
#    ('ID_committee', 'ID Committee Member'),
#    ('admin', 'Admin'),
#    )

MEMBERSHIP_TYPES = (
    ('Individual', 'Individual'),
    ('Family', 'Family'),
    ('Junior', 'Junior'),
    ('Corresponding', 'Corresponding'),
    ('Honorary', 'Honorary'),
    )

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
