from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^base/', include('nimbus.base.urls')),
    (r'^session/', include('nimbus.auth.urls')),
    (r'^users/', include('nimbus.users.urls')),
    (r'^network/', include('nimbus.network.urls')),
    (r'^timezone/', include('nimbus.timezone.urls')),
    (r'^wizard/', include('nimbus.wizard.urls')),
    (r'^computers/', include('nimbus.computers.urls')),
)

if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),  
)
