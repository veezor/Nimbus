from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from gateway.nimbusgate.views import handler

urlpatterns = patterns('gateway.nimbusgate.views',
    url(r'json/get$', handler.get),
    url(r'json/put$', handler.put),
    url(r'json/delete$', handler.delete),
    url(r'json/list$', handler.list),
    url(r'json/plan_size$', handler.get_plan_size),
    url(r'check_auth$', handler.check_auth),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
