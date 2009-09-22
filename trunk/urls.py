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
    # TODO: Reorganizar configurações de networkconfig.
    # Adequar com menu system.
    # views_app/networkinterfaces.py
    (r'^networkinterface/edit$', 'edit_networkinterface'),
    (r'^networkinterface/update$', 'update_networkinterface'),   
    # TODO: Reorganizar configurações.
    # Adequar com menu system.
    # views_app/configs.py
    (r'^config/edit$', 'edit_config'),
    (r'^config/(?P<config_type>.*?)/edit$', 'edit_config'),
    (r'^password/new$', 'new_password'),
    (r'^password/$', 'change_password'),
    (r'^offsite/edit$', 'edit_offsite_config'),
    (r'^offsite/enable$', 'enable_offsite'),
    (r'^offsite/disable$', 'disable_offsite'),
    # views_app/stats.py
    (r'^statistics/main$', 'main_statistics'),
    (r'^statistics/history$', 'history_statistics'),    
    # views_app/authentications.py
    (r'^session/$', 'create_session'),
    (r'^session/new$', 'new_session'),
    (r'^session/delete$', 'delete_session'),
    # views_app/computers.py
    (r'^computer/(?P<comp_id>\d+)$', 'view_computer'),
    (r'^computer/(?P<comp_id>\d+)/edit$', 'edit_computer'),
    (r'^computer/(?P<comp_id>\d+)/update$', 'update_computer'),
    (r'^computer/(?P<comp_id>\d+)/delete$', 'delete_computer'),
    (r'^computer/(?P<comp_id>\d+)/test$', 'test_computer'),
    (r'^computer/(?P<comp_id>\d+)/config/$', 'view_computer_config'),
    (r'^computer/(?P<comp_id>\d+)/config/dump$', 'dump_computer_config'),
    # views_app/storages.py
    (r'^storage/create$', 'create_storage'),
    (r'^storage/new$', 'new_storage'),
    (r'^storage/(?P<sto_id>\d+)$', 'view_storage'),
    (r'^storage/(?P<sto_id>\d+)/edit$', 'edit_storage'),
    (r'^storage/(?P<sto_id>\d+)/update$', 'update_storage'),
    (r'^storage/(?P<sto_id>\d+)/delete$', 'delete_storage'),
    (r'^storage/(?P<sto_id>\d+)/config/$', 'view_storage_config'),
    (r'^storage/(?P<sto_id>\d+)/config/dump$', 'dump_storage_config'),
    # views_app/procedures.py
    (r'^procedure/(?P<proc_id>\d+)/edit$', 'edit_procedure'),
    (r'^procedure/(?P<proc_id>\d+)/update$', 'update_procedure'),
    (r'^procedure/(?P<proc_id>\d+)/delete$', 'delete_procedure'),
    # views_app/filesets.py
    (r'^fileset/(?P<fset_id>\d+)/delete$', 'delete_fileset'),
    # views_app/schedules.py
    (r'^schedule/(?P<sched_id>\d+)/edit$', 'edit_schedule'),
    (r'^schedule/(?P<sched_id>\d+)/update$', 'update_schedule'),
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
    # nas etapas e os objetos só serão salvos ao final do wizard.
    # Também separar o wizard em mais de um view object.
    # Novo Design da Funcionalidade de Cadastro de Backup:
    # PASSO 1: Onde
    (r'^backup/new$', 'new_backup'),
    # PASSO 2: Oque
    (r'^computer/(?P<comp_id>\d+)/backup/new$', 'new_backup'),
    # PASSO 3: Quando
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/backup/new$', 'new_backup'),
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
    (r'^computer/(?P<comp_id>\d+)/procedure/(?P<proc_id>\d+)/job/(?P<job_id>\d+)/restore/new$', 'restore_files'),    
    # Tools
    (r'^tools/$', 'view_tools'),
    (r'^tools/ssl/$', 'tools_ssl'),
#    (r'^admin/(.*)', admin.site.root),
)