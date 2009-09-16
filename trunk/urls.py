from os.path import dirname

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
base_url = 'backup_corporativo'

urlpatterns = patterns('',
    (r'^$', 'backup_corporativo.bkp.views.view_stats'),
    (r'^static/(?P<path>.*)', 'django.views.static.serve',
        {'document_root': '%s/templates/bkp/static' % dirname(__file__)}),
    # management
    (r'^management/$', 'backup_corporativo.bkp.views.view_management'),
    (r'^management/computers/$', 'backup_corporativo.bkp.views.view_computers'),
    (r'^management/storages/$', 'backup_corporativo.bkp.views.view_storages'),
    # views_app/configs.py
    (r'^config/edit$', 'backup_corporativo.bkp.views.edit_config'),
    (r'^config/(?P<config_type>.*?)/edit$', 'backup_corporativo.bkp.views.edit_config'),
    (r'^password/new$', 'backup_corporativo.bkp.views.new_password'),
    (r'^password/$', 'backup_corporativo.bkp.views.change_password'),
    (r'^offsite/edit$', 'backup_corporativo.bkp.views.edit_offsite_config'),
    (r'^offsite/enable$', 'backup_corporativo.bkp.views.enable_offsite'),
    (r'^offsite/disable$', 'backup_corporativo.bkp.views.disable_offsite'),
    # views_app/networkinterfaces.py
    (r'^networkinterface/edit$', 'backup_corporativo.bkp.views.edit_networkinterface'),
    (r'^networkinterface/update$', 'backup_corporativo.bkp.views.update_networkinterface'),   
    # views_app/stats.py
    (r'^stats$', 'backup_corporativo.bkp.views.view_stats'),
    # views_app/authentications.py
    (r'^session/$', 'backup_corporativo.bkp.views.create_session'),
    (r'^session/new$', 'backup_corporativo.bkp.views.new_session'),
    (r'^session/delete$', 'backup_corporativo.bkp.views.delete_session'),
    # views_app/computers.py
    (r'^computer/(?P<computer_id>\d+)$', 'backup_corporativo.bkp.views.view_computer'),
    (r'^computer/(?P<computer_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_computer'),
    (r'^computer/(?P<computer_id>\d+)/update$', 'backup_corporativo.bkp.views.update_computer'),
    (r'^computer/(?P<computer_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_computer'),
    (r'^computer/(?P<computer_id>\d+)/test$', 'backup_corporativo.bkp.views.test_computer'),
    (r'^computer/(?P<computer_id>\d+)/config/$', 'backup_corporativo.bkp.views.view_computer_config'),
    (r'^computer/(?P<computer_id>\d+)/config/dump$', 'backup_corporativo.bkp.views.dump_computer_config'),
    # views_app/storages.py
    (r'^storage/$', 'backup_corporativo.bkp.views.create_storage'),
    (r'^storage/new$', 'backup_corporativo.bkp.views.new_storage'),
    (r'^storage/(?P<storage_id>\d+)$', 'backup_corporativo.bkp.views.view_storage'),
    (r'^storage/(?P<storage_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_storage'),
    (r'^storage/(?P<storage_id>\d+)/update$', 'backup_corporativo.bkp.views.update_storage'),
    (r'^storage/(?P<storage_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_storage'),
    (r'^storage/(?P<storage_id>\d+)/config/$', 'backup_corporativo.bkp.views.view_storage_config'),
    (r'^storage/(?P<storage_id>\d+)/config/dump$', 'backup_corporativo.bkp.views.dump_storage_config'),
    # views_app/procedures.py
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/update$', 'backup_corporativo.bkp.views.update_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_procedure'),
    # views_app/filesets.py
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/fileset/(?P<fileset_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_fileset'),
    # views_app/schedules.py
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/update$', 'backup_corporativo.bkp.views.update_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_schedule'),
    # Novo Design da Funcionalidade de Cadastro de Backup:
    (r'^backup/new$', 'backup_corporativo.bkp.views.new_backup'),    # PASSO 1: Onde
    (r'^computer/(?P<computer_id>\d+)/backup/new$', 'backup_corporativo.bkp.views.new_backup'),    # PASSO 2: Oque
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/backup/new$', 'backup_corporativo.bkp.views.new_backup'),    # PASSO 3: Quando
    # Novo Design da Funcionalidade do Restore:
    (r'^restore/new$', 'backup_corporativo.bkp.views.new_restore'),     # PASSO 1: Selecione Computador
    (r'^computer/(?P<computer_id>\d+)/restore/new$', 'backup_corporativo.bkp.views.new_restore'),       # PASSO 2: Selecione Procedimento
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/restore/new$', 'backup_corporativo.bkp.views.new_restore'),    # PASSO 3: Selecione Data
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/job/(?P<job_id>\d+)/restore/new$', 'backup_corporativo.bkp.views.new_restore'),    # PASSO 4: Selecione Arquivos e Detalhes do Restore
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/job/(?P<job_id>\d+)/restore/new$', 'backup_corporativo.bkp.views.restore_files'),    # PASSO 5: Execute!
    # Tools
    (r'^tools/$', 'backup_corporativo.bkp.views.view_tools'),
    (r'^tools/ssl/$', 'backup_corporativo.bkp.views.tools_ssl'),
    (r'^admin/(.*)', admin.site.root),
)