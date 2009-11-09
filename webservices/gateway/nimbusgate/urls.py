from django.conf.urls.defaults import *
from views import handler

urlpatterns = patterns('gateway.nimbusgate.views',
    url(r'json/get/key/(?P<key>\w+)/$', handler.get),
    url(r'json/put/key/(?P<key>\w+)/base64/(?P<base64_of_md5>\w+)/$', handler.put),
    url(r'json/delete/key/(?P<key>\w+)/$', handler.delete),
    url(r'json/list/$', handler.list),
)
