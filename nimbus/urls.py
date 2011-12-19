from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

if settings.DEBUG:
    admin.autodiscover()

def modular_app_patterns():
    apps = settings.MODULAR_APPS
    pattern_list = []
    for app in apps:
        if app.startswith('nimbus.'):
            app_name = app.split('.')[-1]
            pattern_list.append((r'^%s/' % app_name, include('%s.urls' % app)))
    return pattern_list

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
    # (r'^backup/', include('nimbus.backup.urls')),
    (r'^procedures/', include('nimbus.procedures.urls')),
    (r'^system/', include('nimbus.system.urls')),
    (r'^filesets/', include('nimbus.filesets.urls')),
    (r'^schedules/', include('nimbus.schedules.urls')),
    (r'^reports/', include('nimbus.reports.urls')),
    (r'^LICENSE/', 'nimbus.base.views.license'),
)
for app in modular_app_patterns():
    urlpatterns += patterns('',
    app,)
    
if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),  
)


if settings.DEBUG:
    urlpatterns += patterns('',
    ('^admin/', include(admin.site.urls)),
)
