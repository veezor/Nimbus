from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
base_url = 'backup_corporativo'

urlpatterns = patterns('',
    # Restore
    (r'^computer/(?P<computer_id>\d+)/restore/(.*)', 'backup_corporativo.bkp.views.do_restore'),
    # Cadastro Completo
    (r'^backup/new$', 'backup_corporativo.bkp.views.new_backup'),
    (r'^backup/create$', 'backup_corporativo.bkp.views.create_backup'),
    # Device externo
    (r'^device/new$', 'backup_corporativo.bkp.views.new_device'),
    (r'^device/create$', 'backup_corporativo.bkp.views.create_device'),
    # Index
    (r'^$', 'backup_corporativo.bkp.views.list_computers'),
    # Arquivos estaticos.
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': '/home/jonatas/Projects/bc-devel/backup_corporativo/templates/bkp/static'}),
    # Global Config
    (r'^config/edit$', 'backup_corporativo.bkp.views.edit_config'),
    # Dump
    (r'^dump/create$', 'backup_corporativo.bkp.views.create_dump'),        
    (r'^dump/restore$', 'backup_corporativo.bkp.views.restore_dump'),
    # Stats
    (r'^stats$', 'backup_corporativo.bkp.views.view_stats'),
    # session [NEW, DELETE, CREATE]
    (r'^session/new$', 'backup_corporativo.bkp.views.new_session'),
    (r'^session/delete$', 'backup_corporativo.bkp.views.delete_session'),
    (r'^session/$', 'backup_corporativo.bkp.views.create_session'),
    # computer [VIEW, EDIT, DELETE, CREATE]
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
    # trigger [CREATE WTRIGGER, CREATE MTRIGGER]
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/weeklytrigger/$', 'backup_corporativo.bkp.views.weeklytrigger'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/monthlytrigger/$', 'backup_corporativo.bkp.views.monthlytrigger'),
    (r'^admin/(.*)', admin.site.root),
)
