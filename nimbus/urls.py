from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

if settings.DEBUG:
    admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', include('nimbus.base.urls')),
    (r'^base/', include('nimbus.base.urls')),
    (r'^session/', include('nimbus.session.urls')),
    (r'^users/', include('nimbus.users.urls')),
    (r'^network/', include('nimbus.network.urls')),
    (r'^timezone/', include('nimbus.timezone.urls')),
    (r'^wizard/', include('nimbus.wizard.urls')),
    (r'^computers/', include('nimbus.computers.urls')),
    (r'^storages/', include('nimbus.storages.urls')),
    (r'^restore/', include('nimbus.restore.urls')),
    (r'^recovery/', include('nimbus.recovery.urls')),
    # (r'^backup/', include('nimbus.backup.urls')),
    (r'^offsite/', include('nimbus.offsite.urls')),
    (r'^procedures/', include('nimbus.procedures.urls')),
    (r'^system/', include('nimbus.system.urls')),
    (r'^filesets/', include('nimbus.filesets.urls')),
    (r'^schedules/', include('nimbus.schedules.urls')),
    (r'^reports/', include('nimbus.reports.urls')),
    (r'^LICENSE/', 'nimbus.base.views.license'),
)

if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),  
)


if settings.DEBUG:
    urlpatterns += patterns('',
    ('^admin/', include(admin.site.urls)),
)
