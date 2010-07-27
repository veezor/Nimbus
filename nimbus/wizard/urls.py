from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.wizard.views',
    (r'^start/$', 'start'), 
    (r'^network/$', 'network'), 
    (r'^finish/$', 'finish'), 
    (r'^password/$', 'password'), 
    (r'^timezone/$', 'timezone'), 
    (r'^offsite/$', 'offsite'), 
)
