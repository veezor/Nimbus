from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.wizard.views',
    (r'^(?P<step>\w+)/$', 'wizard'),
    (r'^(?P<step>\w+)/next/$', 'wizard_next'),
    (r'^(?P<step>\w+)/previous/$', 'wizard_previous'),
    (r'^$', 'wizard', {"step": "start"}),
)
