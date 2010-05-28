#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

from backup_corporativo.bkp import views

base_url = 'backup_corporativo'

# Declarando primeiro a rota estática, que no futuro será removida
# já que o conteúdo estático será servido pelo próprio servidor
# web seja lá qual for que o Nimbus utilize
#urlpatterns = patterns(
#    '',
#    (r'^static/(?P<path>.*)', 'django.views.static.serve', {
#        'document_root':'%s/templates/bkp/static' % dirname(__file__)}))

# O resto das rotas é declarado separadamente
# já que todas tem o prefixo 'backup_corporativo.bkp.views'
# em comum.
urlpatterns = patterns(
    'backup_corporativo.bkp.views',
    (r'^$', 'main_statistics'),
    # management
    (r'^management/$', 'main_management'),
    (r'^management/computers/list$', 'list_computers'),
    (r'^management/storages/list$', 'list_storages'),
    (r'^management/encryptions/list$', 'list_encryptions'),
    (r'^management/encryptions/new$', 'new_encryption'),
    (r'^management/encryptions/create$', 'create_encryption'),
    #(r'^management/encryptions/remove$', 'remove_encryptions'),
    #(r'^management/encryptions/delete$', 'delete_encryptions'),    
    # TODO: tirar strongbox de management
    (r'^management/strongbox/$', 'manage_strongbox'),
    (r'^management/strongbox/new$', 'new_strongbox'),
    (r'^management/strongbox/create$', 'create_strongbox'),
    (r'^management/strongbox/mount$', 'mount_strongbox'),
    (r'^management/strongbox/umount$', 'umount_strongbox'),
    (r'^management/strongbox/changepwd$', 'changepwd_strongbox'),
    (r'^strongbox/headerbkp/list$', 'list_headerbkp'),
    (r'^strongbox/headerbkp/new$', 'new_headerbkp'),
    (r'^strongbox/headerbkp/create$', 'create_headerbkp'),
    (r'^strongbox/headerbkp/(?P<hbkp_id>\d+)/delete$', 'delete_headerbkp'),
    (r'^strongbox/headerbkp/(?P<hbkp_id>\d+)/edit$', 'edit_headerbkp'),
    (r'^strongbox/headerbkp/(?P<hbkp_id>\d+)/update$', 'update_headerbkp'),
    (r'^strongbox/headerbkp/(?P<hbkp_id>\d+)/restore$', 'restore_headerbkp'),
    # system
    (r'^system/$', 'main_system'),
    (r'^system/time/$', 'manage_system_time'),
    (r'^system/time/ajax_area_request$', 'ajax_area_request'),
    (r'^system/time/update$', 'update_system_time'),    
    (r'^system/network/$', 'manage_system_network'),
    (r'^system/network/update$', 'update_system_network'),
    (r'^system/network/ping/create$', 'create_ping'),
    (r'^system/network/traceroute/create$', 'create_traceroute'),
    (r'^system/network/nslookup/create$', 'create_nslookup'),
    (r'^system/config/edit$', 'edit_system_config'),
    (r'^system/config/update$', 'update_system_config'),
    (r'^system/password/edit$', 'edit_system_password'),
    (r'^system/password/update$', 'update_system_password'),
    (r'^system/offsite/edit$', 'edit_system_offsite'),
    (r'^system/offsite/enable$', 'enable_system_offsite'),
    (r'^system/offsite/disable$', 'disable_system_offsite'),
    # views_app/stats.py
    (r'^statistics/computer/$', 'stats_computer'),
    (r'^statistics/procedure/$', 'stats_procedure'),
    (r'^statistics/global/$', 'stats_global'),
    
    (r'^statistics/$', 'main_statistics'),
    (r'^statistics/history/$', 'history_statistics'),    
    # views_app/authentications.py
    (r'^session/$', 'create_session'),
    (r'^session/new$', 'new_session'),
    (r'^session/delete$', 'delete_session'),
    # views_app/computers.py
    (r'^computer/new$', 'new_computer'),
    (r'^computer/create$', 'create_computer'),
    (r'^computer/(?P<comp_id>\d+)$', 'view_computer'),
    (r'^computer/(?P<comp_id>\d+)/edit$', 'edit_computer'),
    (r'^computer/(?P<comp_id>\d+)/update$', 'update_computer'),
    (r'^computer/(?P<comp_id>\d+)/delete$', 'delete_computer'),
    (r'^computer/(?P<comp_id>\d+)/test$', 'test_computer'),
    (r'^computer/(?P<comp_id>\d+)/config/$', 'view_computer_config'),
    (r'^computer/(?P<comp_id>\d+)/backup/new$', 'new_computer_backup'),        
    (r'^computer/(?P<comp_id>\d+)/backup/create$', 'create_computer_backup'),
    (r'^computer/(?P<comp_id>\d+)/file/dump$', 'dump_computer_file'),        
    # views_app/procedures.py
    (r'^procedure/(?P<proc_id>\d+)/backup/edit$', 'edit_backup'),
    (r'^procedure/(?P<proc_id>\d+)/backup/update$', 'update_backup'),
    (r'^procedure/(?P<proc_id>\d+)/delete$', 'delete_procedure'),
    (r'^procedure/(?P<proc_id>\d+)/fileset/new$', 'new_procedure_fileset'),
    (r'^procedure/(?P<proc_id>\d+)/fileset/create$', 'create_procedure_fileset'),
    (r'^procedure/(?P<proc_id>\d+)/schedule/new$', 'new_procedure_schedule'),
    (r'^procedure/(?P<proc_id>\d+)/schedule/create$', 'create_procedure_schedule'),
    # views_app/filesets.py
    (r'^fileset/(?P<fset_id>\d+)/delete$', 'delete_fileset'),
    # views_app/schedules.py
    (r'^schedule/(?P<sched_id>\d+)/update$', 'update_schedule'),
    (r'^schedule/(?P<sched_id>\d+)/edit$', 'edit_schedule'),
    (r'^schedule/(?P<sched_id>\d+)/delete$', 'delete_schedule'),

    # views_app/wizard.py
    (r'^wizard/$', 'main_wizard'),
    (r'^wizard/config/edit$', 'edit_wizard_config'),
    (r'^wizard/config/update$', 'update_wizard_config'),

    (r'^wizard/network/edit$', 'edit_wizard_network'),
    (r'^wizard/network/update$', 'update_wizard_network'),
    
    (r'^wizard/timezone/edit$', 'edit_wizard_timezone'),
    (r'^wizard/timezone/update$', 'update_wizard_timezone'),
        
    (r'^wizard/strongbox/edit$', 'edit_wizard_strongbox'),
    (r'^wizard/strongbox/update$', 'update_wizard_strongbox'),


    (r'^wizard/confirm$', 'confirm_wizard'),

    # wizard de restore
    (r'^restore/new$', 'new_restore'),
    (r'^restore/create$', 'create_restore'),
    (r'^computer/(?P<comp_id>\d+)/restore/new$', 'new_computer_restore'),
    (r'^computer/(?P<comp_id>\d+)/restore/create$', 'create_computer_restore'),
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/restore/new$', 'new_procedure_restore'),
    #(r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/restore/create$', 'create_procedure_restore'),
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/job/(?P<job_id>\d+)/restore/new$', 'new_job_restore'),
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/job/(?P<job_id>\d+)/restore/create$', 'create_job_restore'),


# external storages
    (r'^system/externalstorage/new$', 'new_or_edit_external_storage',
            None, 'backup_corporativo.bkp.views.new_external_storage'),
    (r'^externalstorage/create$', 'create_or_update_external_storage', 
            None, 'backup_corporativo.bkp.views.create_external_storage'),
    (r'^system/externalstorage/(?P<device_id>\d+)/edit$', 'new_or_edit_external_storage', 
            None, 'backup_corporativo.bkp.views.edit_external_storage'),
    (r'^externalstorage/(?P<device_id>\d+)/update$', 'create_or_update_external_storage', 
            None, 'backup_corporativo.bkp.views.update_external_storage'),
    (r'^system/externalstorages/$', 'list_externalstorages' ),


# offsite

    (r'^offsite/list_downloadrequest', 'list_downloadrequest'),
    (r'^offsite/list_uploadrequest', 'list_uploadrequest'),
    (r'^system/backup/', 'select_storage'),
    (r'^system/backup/copy_files_to_storage', 'copy_files_to_storage'),


# recovery
    (r'^system/recovery/$', 'recovery_start'),
    (r'^system/recovery/select_source', 'recovery_select_source'),
    (r'^system/recovery/select_storage', 'recovery_select_storage'),
    (r'^system/recovery/select_instance_name', 'recovery_select_instance_name'),
    (r'^system/recovery/databases', 'recover_databases'),
    (r'^system/recovery/volumes', 'recover_volumes'),
    (r'^system/recovery/finish', 'recovery_finish'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  )
