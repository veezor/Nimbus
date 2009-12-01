#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import dirname
from django.conf.urls.defaults import *

base_url = 'backup_corporativo'

# Declarando primeiro a rota estática, que no futuro será removida
# já que o conteúdo estático será servido pelo próprio servidor
# web seja lá qual for que o Nimbus utilize
urlpatterns = patterns(
    '',
    (r'^static/(?P<path>.*)', 'django.views.static.serve', {
        'document_root':'%s/templates/bkp/static' % dirname(__file__)}))

# O resto das rotas é declarado separadamente
# já que todas tem o prefixo 'backup_corporativo.bkp.views'
# em comum.
urlpatterns += patterns(
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
    (r'^statistics/main$', 'main_statistics'),
    (r'^statistics/history$', 'history_statistics'),    
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
    (r'^computer/(?P<comp_id>\d+)/config/dump$', 'dump_computer_config'),
    (r'^computer/(?P<comp_id>\d+)/backup/new$', 'new_computer_backup'),        
    (r'^computer/(?P<comp_id>\d+)/backup/create$', 'create_computer_backup'),        
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
    #
    #
    #
    # Próxima parte do código não será organizada porque será refeita
    #
    #
    #
    # TODO: Refazer wizard. Toda a comunicação entre as etapas do
    # novo wizard será feita através de POST, permitindo ida e volta
    # nas etapas.
    # Também separar o wizard em mais de um view object.
    # Novo Design da Funcionalidade do Restore:
    # PASSO 1: Selecione Computador
    (r'^restore/new$', 'new_restore'),
    # PASSO 2: Selecione Procedimento
    (r'^computer/(?P<comp_id>\d+)/restore/new$', 'new_restore'),
    # PASSO 3: Selecione Data
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/restore/new$', 'new_restore'),
    # PASSO 4: Selecione Arquivos e Detalhes do Restore
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/job/(?P<job_id>\d+)/restore/new$', 'new_restore'),
    # PASSO 5: Execute!
    #(r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/job/(?P<job_id>\d+)/restore/new$', 'restore_files'),    
    # Tools
    (r'^tools/$', 'view_tools'),
    (r'^tools/ssl/$', 'tools_ssl'),
#    (r'^admin/(.*)', admin.site.root),
)
