from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
base_url = 'backup_corporativo'

urlpatterns = patterns('',
    (r'^$', 'backup_corporativo.bkp.views.list_computers'), #index
    # Arquivos estaticos.
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/jonatas/Projects/bc-devel/backup_corporativo/templates/bkp/static'}),
    # Global Config
    (r'^config/edit$', 'backup_corporativo.bkp.views.edit_config'),    
    # session [NEW, DELETE, CREATE]
    (r'^session/new$', 'backup_corporativo.bkp.views.new_session'),
    (r'^session/delete$', 'backup_corporativo.bkp.views.delete_session'),        
    (r'^session/$', 'backup_corporativo.bkp.views.create_session'),    
    # computer [LIST, VIEW, EDIT, DELETE, CREATE]
    (r'^computer/(?P<computer_id>\d+)$', 'backup_corporativo.bkp.views.view_computer'),
    (r'^computer/(?P<computer_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_computer'),
    (r'^computer/(?P<computer_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_computer'),
    (r'^computer/$', 'backup_corporativo.bkp.views.create_computer'),
    # procedure [VIEW, EDIT, DELETE, CREATE]
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)$', 'backup_corporativo.bkp.views.view_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_procedure'),    
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/$', 'backup_corporativo.bkp.views.create_procedure'),
    # fileset [CREATE]
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/fileset/$', 'backup_corporativo.bkp.views.create_fileset'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/fileset/(?P<fileset_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_fileset'),    
    # schedule [VIEW, CREATE, DELETE]
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)$', 'backup_corporativo.bkp.views.view_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/$', 'backup_corporativo.bkp.views.create_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_schedule'),
    # trigger [CREATE WTRIGGER, CREATE MTRIGGER, CREATE UTRIGGER]
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/weeklytrigger/$', 'backup_corporativo.bkp.views.weeklytrigger'), # create weeklytrigger
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/monthlytrigger/$', 'backup_corporativo.bkp.views.monthlytrigger'), # create monthlytrigger
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/uniquetrigger/$', 'backup_corporativo.bkp.views.uniquetrigger'), # create uniquetrigger
 
    # Example:
    # (r'^teste/', include('teste.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)
