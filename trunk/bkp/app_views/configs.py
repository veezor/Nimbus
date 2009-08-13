#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import GlobalConfig, Procedure
from backup_corporativo.bkp.models import ExternalDevice
from backup_corporativo.bkp.forms import GlobalConfigForm, OffsiteConfigForm
from backup_corporativo.bkp.forms import RestoreDumpForm
from backup_corporativo.bkp.forms import ExternalDeviceForm
from backup_corporativo.bkp.forms import ExternalDeviceEditForm
from django.contrib.auth.forms import PasswordChangeForm
from backup_corporativo.bkp.models import RestrictionTime
from backup_corporativo.bkp.models import DayOfTheWeek
from backup_corporativo.bkp.models import BandwidthRestriction
from backup_corporativo.bkp.models import RestrictionTime
from backup_corporativo.bkp.forms import BandwidthRestrictionForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Global Config ###
@authentication_required
def edit_config(request, config_type='global'):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    vars_dict['config_type'] = config_type
    vars_dict['request'] = request
    try:
        vars_dict['gconfig'] = GlobalConfig.objects.get(pk=1)    
    except GlobalConfig.DoesNotExist:
        vars_dict['gconfig'] = None

    if request.method == 'GET':
        if config_type:
            if config_type == 'global':
                vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
                forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
            elif config_type == 'dump_restore':
                forms_dict['restoredumpform'] = RestoreDumpForm()
            elif config_type == 'password':
                forms_dict['pwdform'] = PasswordChangeForm(return_dict['current_user'])
            elif config_type == 'devices':
                forms_dict['devform'] = ExternalDeviceForm()
                vars_dict['dev_choices'] = ExternalDevice.device_choices()
                vars_dict['devices'] = ExternalDevice.objects.all()
            elif config_type == 'restrictions':
                vars_dict['rtimes'] = RestrictionTime.objects.all().order_by('restriction_time')
                vars_dict['rests'] = BandwidthRestriction.objects.all().order_by('dayoftheweek','restrictiontime')
                forms_dict['restform'] = BandwidthRestrictionForm()
                vars_dict['days_of_the_week'] = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
            elif config_type == 'offsite':
                vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
                vars_dict['offsite_on'] = vars_dict['gconfig'].offsite_on
                vars_dict['procedures'] = Procedure.objects.filter(offsite_on=True)
                forms_dict['offsiteform'] = OffsiteConfigForm(instance=vars_dict['gconfig'])
        else:
            vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
            forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
            forms_dict['restoredumpform'] = RestoreDumpForm()
            # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit/edit_config.html',return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['gconfigform'] = GlobalConfigForm(request.POST, instance=vars_dict['gconfig'])
        forms_dict['restoredumpform'] = RestoreDumpForm()

        if forms_dict['gconfigform'].is_valid():
            vars_dict['gconfig'] = forms_dict['gconfigform'].save()
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Configurações aplicadas com sucesso.")
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e a configuração não foi alterada.")
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))


### Password Management ###
@authentication_required
def change_password(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['pwdform'] = PasswordChangeForm(return_dict['current_user'], request.POST)
        
        if forms_dict['pwdform'].is_valid():
            request.user.set_password(forms_dict['pwdform'].cleaned_data['new_password1'])
            request.user.save()
            request.user.message_set.create(message="Senha foi alterada com sucesso.")
            return redirect_back_or_default(request, default=root_path(request))
        else:
            vars_dict['config_type'] = 'password'
            # Load forms and vars
            request.user.message_set.create(message="Houve um erro e a senha não foi alterada.")
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))


### Device ###
@authentication_required
def create_device(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['devform'] = ExternalDeviceForm(request.POST)
        if forms_dict['devform'].is_valid():
            dev = ExternalDevice()
            dev.device_name = forms_dict['devform'].cleaned_data['device_name']
            dev.uuid = forms_dict['devform'].cleaned_data['uuid']
            dev.mount_index = ExternalDevice.next_device_index()
            dev.save()
            request.user.message_set.create(message="Dispositivo adicionado com sucesso.")            
            return HttpResponseRedirect(new_device_path(request))
        else:
            vars_dict['dev_choices'] = ExternalDevice.device_choices()
            vars_dict['devices'] = ExternalDevice.objects.all()
            vars_dict['config_type'] = 'devices'
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))
            
@authentication_required
def edit_device(request, device_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        vars_dict['dev'] = get_object_or_404(ExternalDevice, pk=device_id)
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit/edit_device.html', return_dict, context_instance=RequestContext(request))
    if request.method == 'POST':
        dev = get_object_or_404(ExternalDevice, pk=device_id)
        forms_dict['devform'] = ExternalDeviceEditForm(request.POST)
        if forms_dict['devform'].is_valid():
            dev.device_name = forms_dict['devform'].cleaned_data['device_name']
            dev.save()
            request.user.message_set.create(message="Dispositivo alterado com sucesso.")
            return HttpResponseRedirect(new_device_path(request))
        else:
            vars_dict['dev'] = get_object_or_404(ExternalDevice, pk=device_id)
            request.user.message_set.create(message="Existem erros e o dispositivo não foi alterado.")
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/edit/edit_device.html', return_dict, context_instance=RequestContext(request))
            

@authentication_required
def delete_device(request, device_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['dev'] = get_object_or_404(ExternalDevice, pk=device_id)
        request.user.message_set.create(message="Confirme a remoção do dispositivo.")
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/delete/delete_device.html', return_dict, context_instance=RequestContext(request))
    if request.method == 'POST':
        dev = get_object_or_404(ExternalDevice, pk=device_id)
        dev.delete()
        request.user.message_set.create(message="Dispositivo foi permanentemente removido.")
        return HttpResponseRedirect(new_device_path(request))


### Dump ###
@authentication_required
def create_dump(request):
    from time import strftime
    from backup_corporativo.bkp.crypt_utils import encrypt, decrypt
    from backup_corporativo.settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME
    try:
        from backup_corporativo.settings import BACULA_DB_NAME
    except:
        raise('Could not import BACULA_DB_NAME from settings.py')
   
	# Create dump file and encrypt 
    date = strftime("%Y-%m-%d_%H:%M:%S")
    tmpdump_file = absolute_file_path('tmpdump','custom')
    dump_file = absolute_file_path('%s.nimbus' % date,'custom')
    cmd = '''mysqldump --user=%s --password=%s --add-drop-database --create-options --disable-keys --databases %s %s -r "%s"''' % (DATABASE_USER,DATABASE_PASSWORD,DATABASE_NAME,BACULA_DB_NAME,tmpdump_file)
    os.system(cmd)
    encrypt(tmpdump_file,dump_file,'lala',15,True)
    
	# Return file for download
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.nimbus' % date
    fileHandle = open(dump_file,'r')
    response.write(fileHandle.read())
    fileHandle.close()
    remove_or_leave(dump_file)
    
    return response

@authentication_required
def restore_dump(request):
	vars_dict, forms_dict, return_dict = global_vars(request)
    	try:
        	vars_dict['gconfig'] = GlobalConfig.objects.get(pk=1)
	except GlobalConfig.DoesNotExist:
        	vars_dict['gconfig'] = None

	from backup_corporativo.bkp.crypt_utils import encrypt, decrypt
	from backup_corporativo.settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME

	if request.method == 'POST':
		restore_dump_form = RestoreDumpForm(request.POST, request.FILES)
		if restore_dump_form.is_valid():
			if 'file' in request.FILES:
				file_upload = request.FILES['file']
				crypt_file = absolute_file_path('crypt_dump','custom')
				dec_file = absolute_file_path('dec_dump','custom')

				# Save upload file
				fileHandle = open(crypt_file,'wb')
				fileHandle.write(file_upload.read())
				fileHandle.close()

				# Decrypt file and restore
				decrypt(crypt_file,dec_file,'lala',15)
				cmd = 'mysql --user=%s --password=%s < %s' % (DATABASE_USER, DATABASE_PASSWORD,dec_file)
				os.system(cmd)
				remove_or_leave(dec_file)
				
				request.user.message_set.create(message="Restauração executada com sucesso.")        
				return HttpResponseRedirect(edit_config_path(request))
			else:
				request.user.message_set.create(message="Falha ao realizar UPLOAD do arquivo")        
				return HttpResponseRedirect(edit_config_path(request))
		else:
			request.user.message_set.create(message="Existem erros e a restauração não foi realizada.")
        		vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
        		vars_dict['config_type'] = 'dump_restore'
		        forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
        		forms_dict['restoredumpform'] = restore_dump_form
		        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        		return render_to_response('bkp/edit/edit_config.html',return_dict, context_instance=RequestContext(request))

### Restrictions ###

@authentication_required
def create_restriction(request):
	vars_dict, forms_dict, return_dict = global_vars(request)
    
	if request.method == 'POST':
		restform = BandwidthRestrictionForm(request.POST)
		if restform.is_valid():
			user_rest_value = restform.cleaned_data['restriction_value']
			user_rest_time = restform.cleaned_data['restrictiontime']
			try:
				rtime_object = RestrictionTime.objects.get(restriction_time=user_rest_time)
			except RestrictionTime.DoesNotExist:
				rtime_object = RestrictionTime(restriction_time=user_rest_time)
				rtime_object.save()
			for day in restform.cleaned_data['days']:
				day_object = DayOfTheWeek.objects.get(day_name=day)
				try:
					rest = BandwidthRestriction.objects.get(restrictiontime=rtime_object,dayoftheweek=day_object)
					rest.restriction_value = user_rest_value
					rest.save()
				except BandwidthRestriction.DoesNotExist:
					rest = BandwidthRestriction(dayoftheweek=day_object,restrictiontime=rtime_object,restriction_value=user_rest_value)
					rest.save()
			request.user.message_set.create(message="Restrição de Banda adicionada com sucesso.")
			return HttpResponseRedirect(new_restriction_path(request))
		else:
			request.user.message_set.create(message="O Formulário contém erros.")
			vars_dict['rests'] = BandwidthRestriction.objects.all()
			vars_dict['config_type'] = 'restrictions'
			forms_dict['restform'] = restform
			return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
			return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def delete_restriction(request,restriction_id):
	vars_dict, forms_dict, return_dict = global_vars(request)
	rest = get_object_or_404(BandwidthRestriction,pk=restriction_id)
	if request.method == 'GET':
		vars_dict['rest'] = rest
		request.user.message_set.create(message="Confirme a remoção da restrição.")
		return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
		return render_to_response('bkp/delete/delete_restriction.html', return_dict, context_instance=RequestContext(request))
	if request.method == 'POST':
		request.user.message_set.create(message="Restrição de Banda '%s' removida com sucesso." % rest)
		rest.delete()
		return HttpResponseRedirect(new_restriction_path(request))
		

@authentication_required
def edit_offsite(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    if request.method == 'GET':
        return HttpResponseRedirect(new_offsite_path(request))
    
    if request.method == 'POST':
        forms_dict['offsiteform'] = OffsiteConfigForm(request.POST)
        
        if forms_dict['offsiteform'].is_valid():
            global_config = GlobalConfig.objects.get(pk=1)
            for i in forms_dict['offsiteform'].cleaned_data:
                global_config.__setattr__(i, forms_dict['offsiteform'].cleaned_data[i])
            global_config.save()
            request.user.message_set.create(message="Dados do backup offsite alterados com sucesso.")
            return HttpResponseRedirect(new_offsite_path(request))
        else:
            vars_dict['config_type'] = 'offsite'
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Houve um erro ao tentar alterar os dados do backup offsite.")
            #return HttpResponseRedirect(new_offsite_path(request))
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))

