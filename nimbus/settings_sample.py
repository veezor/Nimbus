# Django settings for nimbus project.

from os.path import join, dirname

DEBUG = True
TEMPLATE_DEBUG = DEBUG
AJAX_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'test.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


### NIMBUS


NIMBUS_WIZARD = True

BCONSOLE_CONF = "/var/nimbus/custom/config/bconsole.conf"

RESTORE_POINT_DEFAULT = "/tmp/bacula-restore"

# Nimbus log verbose
LOG_DEBUG = True

# Static files
SERVE_STATIC_FILES = True


# END NIMBUS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join( dirname(__file__), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/adminmedia/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7qj040(6uwuuzx+y&ety-bs5i$*q$0tag02q+sx8th_%1w$h9%'


LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/session/login"


TEMPLATE_CONTEXT_PROCESSORS = (
    "nimbus.shared.contextprocessors.script_name",
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media" 
)

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
)

if AJAX_DEBUG:
    MIDDLEWARE_CLASSES += ('nimbus.shared.middlewares.AjaxDebug' ,)


if NIMBUS_WIZARD:
    MIDDLEWARE_CLASSES += ('nimbus.wizard.middleware.Wizard' ,)


ROOT_URLCONF = 'nimbus.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'nimbus.auth',
    'nimbus.base',
    'nimbus.users',
    'nimbus.config',
    'nimbus.network',
    'nimbus.schedules',
    'nimbus.timezone',
    'nimbus.offsite',
    'nimbus.wizard',
    'nimbus.computers'
)


