# Django settings for teste project.
import os
import bkp.log

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'nimbus'                  # Or path to database file if using sqlite3.
DATABASE_USER = 'nimbus'             # Not used with sqlite3.
DATABASE_PASSWORD = 'n1mbus'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Bacula config
BACULA_DATABASE_NAME = 'bacula'
BACULA_DATABASE_USER = 'bacula'
BACULA_DATABASE_PASSWORD = 'bacula'
BACULA_DATABASE_HOST = 'localhost'
BACULA_DATABASE_PORT = ''


PYBACULA_TEST = False

NIMBUS_VAR_PATH = '/var/nimbus/'
NIMBUS_BACKUP_PATH = '/var/nimbus/backup/'
NIMBUS_CUSTOM_PATH = '/var/nimbus/custom/'

MAIN_APP = 'backup_corporativo.bkp'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Fortaleza'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-BR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '#6(_m+c4^r)=8fes(yc*xxj5u&ki$9bgdx6y!6)xrtlabd5#5b'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'backup_corporativo.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'templates',
)

FIXTURE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'bkp/app_tests/fixtures'),
)

#DMIGRATIONS_DIR = 'C:/Documents and Settings/Luke/Meus documentos/My Dropbox/Django/Linconet/backup_corporativo/migrations'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'backup_corporativo.bkp',
    #'dmigrations',    
)