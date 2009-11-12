from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from gateway.nimbusgate.views import handler

urlpatterns = patterns('gateway.nimbusgate.views',
    url(r'json/get/key/(?P<key>.*)$', handler.get),
    url(r'json/put/base64/(?P<base64_of_md5>\w+)/key/(?P<key>.*)$', handler.put),
    url(r'json/delete/key/(?P<key>.*)$', handler.delete),
    url(r'json/list$', handler.list),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
