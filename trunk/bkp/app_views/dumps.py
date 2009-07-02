#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


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
			request.user.message_set.create(message="Formulário 'Restaurar Sistema' inválido")
        		vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
		        forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
        		forms_dict['restoredumpform'] = restore_dump_form
		        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        		return render_to_response('bkp/edit_config.html',return_dict, context_instance=RequestContext(request))
