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
    # views_app/configs.py
    (r'^config/edit$', 'backup_corporativo.bkp.views.edit_config'),
    (r'^config/(?P<config_type>.*?)/edit$', 'backup_corporativo.bkp.views.edit_config'),
    # views_app/stats.py
    (r'^stats$', 'backup_corporativo.bkp.views.view_stats'),
    # views_app/authentications.py
    (r'^session/$', 'backup_corporativo.bkp.views.create_session'),
    (r'^session/new$', 'backup_corporativo.bkp.views.new_session'),
    (r'^session/delete$', 'backup_corporativo.bkp.views.delete_session'),
    (r'^password/new$', 'backup_corporativo.bkp.views.new_password'),
    (r'^password/$', 'backup_corporativo.bkp.views.change_password'),
    # views_app/devices.py
    (r'^device/$', 'backup_corporativo.bkp.views.create_device'),
    # views_app/dumps.py
    (r'^dump/create$', 'backup_corporativo.bkp.views.create_dump'),        
    (r'^dump/restore$', 'backup_corporativo.bkp.views.restore_dump'),
    # views_app/computers.py
    (r'^computer/$', 'backup_corporativo.bkp.views.create_computer'),
    (r'^computer/new$', 'backup_corporativo.bkp.views.new_computer'),
    (r'^computer/(?P<computer_id>\d+)$', 'backup_corporativo.bkp.views.view_computer'),
    (r'^computer/(?P<computer_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_computer'),
    (r'^computer/(?P<computer_id>\d+)/update$', 'backup_corporativo.bkp.views.update_computer'),
    (r'^computer/(?P<computer_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_computer'),
    (r'^computer/(?P<computer_id>\d+)/restore/$', 'backup_corporativo.bkp.views.do_restore'),
    (r'^computer/(?P<computer_id>\d+)/restore/new?(.*)', 'backup_corporativo.bkp.views.new_restore'),
    (r'^computer/(?P<computer_id>\d+)/test$', 'backup_corporativo.bkp.views.test_computer'),
    # views_app/procedures.py
    (r'^computer/(?P<computer_id>\d+)/procedure/$', 'backup_corporativo.bkp.views.create_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/new$', 'backup_corporativo.bkp.views.new_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/update$', 'backup_corporativo.bkp.views.update_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/run/new$', 'backup_corporativo.bkp.views.new_run_procedure'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/run/$', 'backup_corporativo.bkp.views.create_run_procedure'),
    # views_app/filesets.py
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/fileset/$', 'backup_corporativo.bkp.views.create_fileset'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/fileset/new$', 'backup_corporativo.bkp.views.new_fileset'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/fileset/(?P<fileset_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_fileset'),
    # views_app/schedules.py
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/$', 'backup_corporativo.bkp.views.create_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/new$', 'backup_corporativo.bkp.views.new_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/edit$', 'backup_corporativo.bkp.views.edit_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/update$', 'backup_corporativo.bkp.views.update_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_schedule'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/weeklytrigger/$', 'backup_corporativo.bkp.views.weeklytrigger'),
    (r'^computer/(?P<computer_id>\d+)/procedure/(?P<procedure_id>\d+)/schedule/(?P<schedule_id>\d+)/monthlytrigger/$', 'backup_corporativo.bkp.views.monthlytrigger'),
	# views_app/bandwidthrestriction
	(r'restriction/new$', 'backup_corporativo.bkp.views.new_bandwidth_restriction'),
	(r'restriction/(?P<bandwidthrestriction_id>\d+)/delete$', 'backup_corporativo.bkp.views.delete_bandwidth_restriction'),
    (r'^admin/(.*)', admin.site.root),
)
