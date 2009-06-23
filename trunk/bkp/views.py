#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO:
# Falta tratar erros URL caso o ID esteja faltando 
# Validar gatilho c/ tipo de agendamento

# Models
from backup_corporativo.bkp.models import GlobalConfig
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.models import WeeklyTrigger
from backup_corporativo.bkp.models import MonthlyTrigger
from backup_corporativo.bkp.models import FileSet
from backup_corporativo.bkp.models import ExternalDevice
from backup_corporativo.bkp.forms import BandwidthRestriction
# Forms
from backup_corporativo.bkp.forms import GlobalConfigForm
from backup_corporativo.bkp.forms import RestoreDumpForm
from backup_corporativo.bkp.forms import LoginForm
from backup_corporativo.bkp.forms import ComputerForm
from backup_corporativo.bkp.forms import ProcedureForm
from backup_corporativo.bkp.forms import ScheduleForm
from backup_corporativo.bkp.forms import WeeklyTriggerForm
from backup_corporativo.bkp.forms import MonthlyTriggerForm
from backup_corporativo.bkp.forms import FileSetForm
from backup_corporativo.bkp.forms import ExternalDeviceForm
from backup_corporativo.bkp.forms import RestoreForm
from backup_corporativo.bkp.forms import ProcedureAuxForm
from backup_corporativo.bkp.forms import ComputerAuxForm
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import os
# Vars
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, DAYS_OF_THE_WEEK


###
###   Decorators and Global Definitions
###

def global_vars(request):
    """Declare system-wide variables."""
    vars_dict = {}; forms_dict = {}; return_dict = {}
    return_dict['script_name'] = request.META['SCRIPT_NAME']
    return_dict['current_user'] = request.user
    # List of computers.
    vars_dict['comps'] = Computer.objects.all()
    # List of forms.
    forms_dict['compform'] = ComputerForm()
    forms_dict['procform'] = ProcedureForm()
    forms_dict['fsetform'] = FileSetForm()
    forms_dict['schedform'] = ScheduleForm()
    # List of vars.    
    vars_dict['TYPE_CHOICES'] = TYPE_CHOICES
    vars_dict['LEVEL_CHOICES'] = LEVEL_CHOICES
    vars_dict['DAYS_OF_THE_WEEK'] = DAYS_OF_THE_WEEK
    
    return vars_dict, forms_dict, return_dict


def require_authentication(request):
    """Redirect user to authentication page."""
    return HttpResponseRedirect(__login_path(request))


def authentication_required(view_def):
    """Decorator to force a view to verify if user is authenticated."""
    def check_auth(*args, **kw):
        if not args[0].user.is_authenticated():
            return require_authentication(args[0])
        return view_def(*args, **kw)
    check_auth.__name__ = view_def.__name__
    check_auth.__doc__ = view_def.__doc__
    return check_auth


###
###   Views
###

### Do Restore ###
@authentication_required
def do_restore(request, computer_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer, pk=computer_id)
        restore_form = RestoreForm(request.POST)

        if restore_form.is_valid():
            job_id = restore_form.cleaned_data['job_id']
            client_source = restore_form.cleaned_data['client_source']
            client_restore = restore_form.cleaned_data['client_restore']
            comp.run_restore_job(client_source, client_restore, job_id, 'c:/restore/')
        else:
            __redirect_back_or_default(request,__root_path(request))
    
        return HttpResponse("restaura aí, vai!")




### Device ###
@authentication_required
def new_device(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        forms_dict['devform'] = ExternalDeviceForm()
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_device.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_device(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['devform'] = ExternalDeviceForm(request.POST)
        
        if forms_dict['devform'].is_valid():
            forms_dict['devform'].save()
            request.user.message_set.create(message="Device adicionado com sucesso.")            
            return HttpResponseRedirect(__root_path(request))
        else:
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/new_device.html', return_dict, context_instance=RequestContext(request))




### Backup ###
@authentication_required
def new_backup(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        # Load forms and vars
        forms_dict['compauxform'] = ComputerAuxForm()
        forms_dict['mtriggform'] = MonthlyTriggerForm()
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_backup.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_backup(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        temp_dict['compauxform'] = ComputerAuxForm(request.POST)

        if temp_dict['compauxform'].is_valid():
            forms_dict['compform'] = ComputerForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['Procedure']:
                forms_dict['procform'] = ProcedureForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['FileSet']:
                forms_dict['fsetform'] = FileSetForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['Schedule']:
                forms_dict['schedform'] = ScheduleForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['Trigger']:
                triggclass = globals()["%sTriggerForm" % temp_dict['compauxform'].cleaned_data['schedule_type']]
                forms_dict['mtriggform'] = triggclass(request.POST)
            forms_list = forms_dict.values()
            if all([form.is_valid() for form in forms_dict.values()]):
                comp = forms_dict['compform'].save(commit=False)
                proc = forms_dict['procform'].save(commit=False)
                fset = forms_dict['fsetform'].save(commit=False)
                sched = forms_dict['schedform'].save(commit=False)
                trigg = forms_dict['mtriggform'].save(commit=False)
                import pdb; pdb.set_trace()
                comp.save()
                comp.build_backup(proc, fset, sched, trigg)
                request.user.message_set.create(message="Computador cadastrado com sucesso.")
                return HttpResponseRedirect(__computer_path(request, comp.id))
            else:
                # Load forms and vars
                request.user.message_set.create(message="Existem erros e o computador não foi cadastrado.")
                return_dict = __merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
                return render_to_response('bkp/new_backup.html', return_dict, context_instance=RequestContext(request))

### Dump ###
@authentication_required
def create_dump(request):
    from backup_corporativo.bkp.crypt_utils import encrypt, decrypt
    from backup_corporativo.settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME
    from time import strftime
   
	# Create dump file and encrypt 
    date = strftime("%Y-%m-%d_%H:%M:%S")
    tmpdump_file = absolute_file_path('tmpdump','custom')
    dump_file = absolute_file_path('systemdump.nimbus.%s' % date,'custom')
    cmd = '''mysqldump --user=%s --password=%s --add-drop-database --create-options --disable-keys --databases %s bacula -r "%s"''' % (DATABASE_USER,DATABASE_PASSWORD,DATABASE_NAME,tmpdump_file)
    os.system(cmd)
    encrypt(tmpdump_file,dump_file,'lala',15,True)
    
	# Return file for download
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=systemdump.nimbus.%s' % date
    fileHandle = open(dump_file,'r')
    response.write(fileHandle.read())
    fileHandle.close()
    remove_or_leave(dump_file)
    
    return response

@authentication_required
def restore_dump(request):
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
				return HttpResponseRedirect(__edit_config_path(request))
			else:
				request.user.message_set.create(message="Falha ao realizar UPLOAD do arquivo")        
				return HttpResponseRedirect(__edit_config_path(request))
		else:
			request.user.message_set.create(message="Formulário inválido")
			return HttpResponseRedirect(__edit_config_path(request))


### Stats ###
@authentication_required
def view_stats(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    # TODO: remove following chunk of code from view!
    import MySQLdb
    runningjobs_query = ''' select j.Name, jc.Name, j.Level, j.StartTime, j.EndTime, \
                        j.JobFiles, j.JobBytes , JobErrors, JobStatus from Job as j \
                        INNER JOIN Client as jc on j.ClientId = jc.ClientId \
                        WHERE j.JobStatus = 'R' or j.JobStatus = 'p' or j.JobStatus = 'j' \
                        or j.JobStatus = 'c' or j.JobStatus = 'd' or j.JobStatus = 's' \
                        or j.JobStatus = 'M' or j.JobStatus = 'm' or j.JobStatus = 'S' \
                        or j.JobStatus = 'F' or j.JobStatus = 'B'; \
                        '''
    lastjobs_query =   ''' select j.Name, jc.Name, j.Level, j.StartTime, j.EndTime, \
                        j.JobFiles, j.JobBytes , JobErrors, JobStatus \
                        from Job as j INNER JOIN Client as jc \
                        on j.ClientId = jc.ClientId; \
                        '''
    dbsize_query =  ''' SELECT table_schema, 
                    sum( data_length + index_length ) / (1024 * 1024) "DBSIZE" \
                    FROM information_schema.TABLES \
                    WHERE table_schema = 'bacula' \
                    GROUP BY table_schema; \
                    '''
    numproc_query = '''select count(*) "Procedimentos" \
                    from backup_corporativo.bkp_procedure; \
                    '''
    numcli_query =  '''select count(*) "Computadores" \
                    from backup_corporativo.bkp_computer; \
                    '''
    totalbytes_query =  '''select sum(JobBytes) "Bytes" \
                        from Job where Job.JobStatus = 'T'; \
                        '''
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="mysqladmin", db="bacula")
        cursor = db.cursor()
        cursor.execute(runningjobs_query)
        vars_dict['runningjobs'] = cursor.fetchall()
        cursor.execute(lastjobs_query)
        vars_dict['lastjobs'] = cursor.fetchall()
        cursor.execute(dbsize_query)    
        vars_dict['dbsize'] = cursor.fetchall()[0][1]
        cursor.execute(numproc_query)
        vars_dict['numproc'] = int(cursor.fetchall()[0][0])
        cursor.execute(numcli_query)
        vars_dict['numcli'] = int(cursor.fetchall()[0][0])
        cursor.execute(totalbytes_query)
        vars_dict['tbytes'] = cursor.fetchall()[0][0]
    except:
        db = object()
    # Load forms and vars
    return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
    return render_to_response('bkp/view_stats.html', return_dict, context_instance=RequestContext(request))


### Global Config ###
@authentication_required
def edit_config(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    try:
        vars_dict['gconfig'] = GlobalConfig.objects.get(pk=1)    
    except GlobalConfig.DoesNotExist:
        vars_dict['gconfig'] = None

    if request.method == 'GET':
        vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
        forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
        forms_dict['restoredumpform'] = RestoreDumpForm()
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit_config.html',return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['gconfigform'] = GlobalConfigForm(request.POST, instance=vars_dict['gconfig'])
        forms_dict['restoredumpform'] = RestoreDumpForm()

        if forms_dict['gconfigform'].is_valid():
            vars_dict['gconfig'] = forms_dict['gconfigform'].save()
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Configurações aplicadas com sucesso.")
            return render_to_response('bkp/edit_config.html', return_dict, context_instance=RequestContext(request))
        else:
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e a configuração não foi alterada.")
            return render_to_response('bkp/edit_config.html', return_dict, context_instance=RequestContext(request))
       

### Sessions ###
def new_session(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if not request.user.is_authenticated():
        forms_dict['loginform'] = LoginForm()
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_session.html', return_dict, context_instance=RequestContext(request))
    else:
        return __redirect_back_or_default(request, default=__root_path(request))
    

def create_session(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if not request.user.is_authenticated():
        if request.method == 'POST':
            forms_dict['loginform'] = LoginForm(request.POST)
        
            if forms_dict['loginform'].is_valid():
                auth_login = forms_dict['loginform'].cleaned_data['auth_login']
                auth_passwd = forms_dict['loginform'].cleaned_data['auth_password']
                user = authenticate(username=auth_login, password=auth_passwd)
                
                if user:
                    login(request, user)
                    default = GlobalConfig.system_configured(GlobalConfig()) and __root_path(request) or __edit_config_path(request)
                    request.user.message_set.create(message="Bem-vindo ao Sistema de Backups Corporativo.")
                    return __redirect_back_or_default(request, default)
                else:
                    # Load forms and vars
                    return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
                    return render_to_response('bkp/new_session.html', return_dict, context_instance=RequestContext(request))                
            else:
                # Load forms and vars
                return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
                return render_to_response('bkp/new_session.html', return_dict, context_instance=RequestContext(request))
    else:
        return __redirect_back_or_default(request, default=__root_path(request))


def delete_session(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            logout(request)
    return HttpResponseRedirect(__login_path(request))        


### Computers ###
@authentication_required
def list_computers(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    __store_location(request)
    # Load forms and vars
    return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
    return render_to_response('bkp/list_computers.html', return_dict, context_instance=RequestContext(request))

@authentication_required
def edit_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    comp = get_object_or_404(Computer, pk=computer_id)
    if request.method == 'GET': # Edit computer
        forms_dict['compform'] = ComputerForm(instance=comp)
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit_computer.html', return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['compform'] = ComputerForm(request.POST,instance=comp)
        
        if forms_dict['compform'].is_valid():
            forms_dict['compform'].save()
            request.user.message_set.create(message="Computador foi alterado com sucesso.")
            return HttpResponseRedirect(__computer_path(request, comp.id))
        else:
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o computador não foi alterado.")
            return render_to_response('bkp/edit_computer.html', return_dict, context_instance=RequestContext(request))   


@authentication_required
def view_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    __store_location(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer,pk=computer_id)
        vars_dict['procs'] = vars_dict['comp'].procedure_set.all()

        lastjobs_query =   ''' SELECT DISTINCT JobID, FileSet.FileSetId, Client.Name, Job.Name, 
                            Level, JobStatus, StartTime, EndTime, JobFiles, JobBytes , JobErrors
                            from Job, Client, FileSet
                            WHERE Client.Name = '%s'
                            ''' % vars_dict['comp'].computer_name
        import MySQLdb
        try:
            db = MySQLdb.connect(host="localhost", user="root", passwd="mysqladmin", db="bacula")
            cursor = db.cursor()
            cursor.execute(lastjobs_query)
            vars_dict['lastjobs'] = cursor.fetchall()
        except:
            db = object()

        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view_computer.html', return_dict, context_instance=RequestContext(request))    


@authentication_required
def delete_computer(request, computer_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.delete()
        request.user.message_set.create(message="Computador removido permanentemente.")            
        return __redirect_back_or_default(request, default=__root_path(request))  


@authentication_required
def create_computer(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
            forms_dict['compform'] = ComputerForm(request.POST)

            if forms_dict['compform'].is_valid():
                computer = forms_dict['compform'].save()
                request.user.message_set.create(message="Computador cadastrado com sucesso.")
                return HttpResponseRedirect(__computer_path(request, computer.id))
            else:
                # Load forms and vars
                return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
                request.user.message_set.create(message="Existem erros e o computador não foi adicionado.")
                return render_to_response('bkp/list_computers.html', return_dict, context_instance=RequestContext(request))


### Procedure ###
@authentication_required
def edit_procedure(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)

    if request.method == 'GET':
        forms_dict['procform'] = ProcedureForm(instance=vars_dict['proc'])
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit_procedure.html', return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['procform'] = ProcedureForm(request.POST,instance=vars_dict['proc'])
        
        if forms_dict['procform'].is_valid():
            forms_dict['procform'].save()
            request.user.message_set.create(message="O procedimento foi alterado com sucesso.")
            return HttpResponseRedirect(__computer_path(request, computer_id))
        else:
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o procedimento não foi alterado.")
            return render_to_response('bkp/edit_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def view_procedure(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    __store_location(request)
    
    if request.method == 'GET':
        if procedure_id:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = vars_dict['comp'].procedures_list()
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['scheds'] = vars_dict['proc'].schedules_list()
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/view_procedure.html', return_dict, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(__computer_path(request, computer_id))
    

@authentication_required
def new_procedure(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    forms_dict['triggform'] = MonthlyTriggerForm()
    forms_dict['procauxform'] = ProcedureAuxForm()

    if request.method == 'GET':
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_procedure(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        del(forms_dict['compform']) # remove form
        temp_dict['procauxform'] = ProcedureAuxForm(request.POST)

        if temp_dict['procauxform'].is_valid():
            forms_dict['procform'] = ProcedureForm(request.POST)
            if temp_dict['procauxform'].cleaned_data['FileSet']:
                forms_dict['fsetform'] = FileSetForm(request.POST)
            if temp_dict['procauxform'].cleaned_data['Schedule']:
                forms_dict['schedform'] = ScheduleForm(request.POST)
            if temp_dict['procauxform'].cleaned_data['Trigger']:
                triggclass = globals()["%sTriggerForm" % temp_dict['procauxform'].cleaned_data['schedule_type']]
                forms_dict['triggform'] = triggclass(request.POST)
            forms_list = forms_dict.values()
            if all([form.is_valid() for form in forms_dict.values()]):
                proc = forms_dict['procform'].save(commit=False)
                fset = forms_dict['fsetform'].save(commit=False)
                sched = forms_dict['schedform'].save(commit=False)
                trigg = forms_dict['triggform'].save(commit=False)
                proc.computer_id = computer_id
                proc.save()
                proc.build_backup(fset, sched, trigg)
                request.user.message_set.create(message="Procedimento cadastrado com sucesso.")
                return HttpResponseRedirect(__computer_path(request, computer_id))
            else:
                # Load forms and vars
                vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
                request.user.message_set.create(message="Existem erros e o procedimento não foi cadastrado.")
                return_dict = __merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
                return render_to_response('bkp/new_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def delete_procedure(request, computer_id, procedure_id):
    if request.method == 'POST':
        proc = get_object_or_404(Procedure, pk=procedure_id)
        proc.delete()
        request.user.message_set.create(message="Procedimento removido permanentemente.")
        return __redirect_back_or_default(request, default=__computer_path(request, computer_id))


### Schedule ###
@authentication_required
def view_schedule(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    __store_location(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        vars_dict['procs'] = Procedure.objects.filter(computer=vars_dict['comp'])
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        vars_dict['sched_lower_type'] = vars_dict['sched'].type.lower()
        vars_dict['scheds'] = Schedule.objects.filter(procedure=vars_dict['proc'])
        vars_dict['fsets'] = vars_dict['proc'].filesets_list()
        
        # TODO: optmize following chunk of code
        if (vars_dict['sched'].type == 'Weekly'):
            try:
                vars_dict['trigger'] = WeeklyTrigger.objects.get(schedule=vars_dict['sched'])
                forms_dict['triggerform'] = WeeklyTriggerForm(instance=vars_dict['trigger'])
                vars_dict['triggerformempty'] = False
            except WeeklyTrigger.DoesNotExist:
                forms_dict['triggerform'] = WeeklyTriggerForm()
                vars_dict['triggerformempty'] = True
        elif (vars_dict['sched'].type == 'Monthly'):
            try:
                vars_dict['trigger'] = MonthlyTrigger.objects.get(schedule=vars_dict['sched'])
                forms_dict['triggerform'] = MonthlyTriggerForm(instance=vars_dict['trigger'])                
                vars_dict['triggerformempty'] = False
            except MonthlyTrigger.DoesNotExist:
                forms_dict['triggerform'] = MonthlyTriggerForm()                
                vars_dict['triggerformempty'] = True
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view_schedule.html', return_dict, context_instance=RequestContext(request))       


@authentication_required
def create_schedule(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'POST':
        forms_dict['schedform'] = ScheduleForm(request.POST)
        
        if forms_dict['schedform'].is_valid():
            schedule = Schedule()
            schedule.procedure_id = procedure_id
            schedule.type = forms_dict['schedform'].cleaned_data['type']
            schedule.save()
            request.user.message_set.create(message="Agendamento cadastrado com sucesso.")
            return HttpResponseRedirect(__schedule_path(request, schedule_id, procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = vars_dict['comp'].procedures_list()
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['scheds'] = vars_dict['proc'].schedules_list()
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o agendamento não foi cadastrado.")
            return render_to_response('bkp/view_procedure.html', return_dict, context_instance=RequestContext(request))   


@authentication_required
def delete_schedule(request, computer_id, procedure_id, schedule_id):
    if request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=schedule_id)
        sched.delete()
        request.user.message_set.create(message="Agendamento foi removido permanentemente.")
        return __redirect_back_or_default(request, default=__procedure_path(request, computer_id,procedure_id))
        
        
### Triggers ###
@authentication_required
def weeklytrigger(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        forms_dict['triggerform'] = WeeklyTriggerForm(request.POST)
        
        if forms_dict['triggerform'].is_valid():
            try:
                wtrigger = WeeklyTrigger.objects.get(schedule=vars_dict['sched'])
            except WeeklyTrigger.DoesNotExist:
                wtrigger = WeeklyTrigger()
            wtrigger.schedule_id = schedule_id
            wtrigger.sunday = forms_dict['triggerform'].cleaned_data['sunday']
            wtrigger.monday = forms_dict['triggerform'].cleaned_data['monday']
            wtrigger.tuesday = forms_dict['triggerform'].cleaned_data['tuesday']
            wtrigger.wednesday = forms_dict['triggerform'].cleaned_data['wednesday']
            wtrigger.thursday = forms_dict['triggerform'].cleaned_data['thursday']
            wtrigger.friday = forms_dict['triggerform'].cleaned_data['friday']
            wtrigger.saturday = forms_dict['triggerform'].cleaned_data['saturday']
            wtrigger.hour = forms_dict['triggerform'].cleaned_data['hour']
            wtrigger.level = forms_dict['triggerform'].cleaned_data['level']
            wtrigger.save()
            request.user.message_set.create(message="Agendamento configurado com sucesso.")
            return HttpResponseRedirect(__schedule_path(request, schedule_id, procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = Procedure.objects.filter(computer=vars_dict['comp'])
            vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
            vars_dict['sched_lower_type'] = vars_dict['sched'].type.lower()
            vars_dict['scheds'] = Schedule.objects.filter(procedure=vars_dict['proc'])
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['triggerformempty'] = True
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o agendamento não foi configurado.")
            return render_to_response('bkp/view_schedule.html', return_dict, context_instance=RequestContext(request))        


@authentication_required
def monthlytrigger(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
    
    if request.method == 'POST':
        forms_dict['triggerform'] = MonthlyTriggerForm(request.POST)
        
        if forms_dict['triggerform'].is_valid():
            try:
                mtrigger = MonthlyTrigger.objects.get(schedule=vars_dict['sched'])
            except MonthlyTrigger.DoesNotExist:
                mtrigger = MonthlyTrigger()
            mtrigger.schedule_id = schedule_id
            mtrigger.hour = forms_dict['triggerform'].cleaned_data['hour']
            mtrigger.level = forms_dict['triggerform'].cleaned_data['level']
            mtrigger.target_days = forms_dict['triggerform'].cleaned_data['target_days']
            mtrigger.save()
            request.user.message_set.create(message="Agendamento configurado com sucesso.")
            return HttpResponseRedirect(__schedule_path(request, schedule_id, procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = Procedure.objects.filter(computer=vars_dict['comp'])
            vars_dict['sched_lower_type'] = vars_dict['sched'].type.lower()
            vars_dict['scheds'] = Schedule.objects.filter(procedure=vars_dict['proc'])
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['triggerformempty'] = True
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o agendamento não foi configurado.")
            return render_to_response('bkp/view_schedule.html', return_dict, context_instance=RequestContext(request))                
        
### FileSets ###
@authentication_required
def create_fileset(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['fsetform'] = FileSetForm(request.POST)
        
        if forms_dict['fsetform'].is_valid():
            fileset = FileSet()
            fileset.procedure_id = procedure_id
            fileset.path = forms_dict['fsetform'].cleaned_data['path']
            fileset.save()
            request.user.message_set.create(message="Local cadastrado com sucesso.")
            return HttpResponseRedirect(__procedure_path(request,procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = vars_dict['comp'].procedures_list()
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['scheds'] = vars_dict['proc'].schedules_list()
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o local não foi cadastrado.")
            return render_to_response('bkp/view_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def delete_fileset(request, computer_id, procedure_id, fileset_id):
    if request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fileset_id)
        fset.delete()
        request.user.message_set.create(message="Local foi removido permanentemente.")
        return __redirect_back_or_default(request, default=__procedure_path(request, procedure_id, computer_id))

### Bandwidth Restriction ###
@authentication_required
def new_restriction(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['rests'] = BandwidthRestriction.objects.all()

    if request.method == 'GET':
        forms_dict['restform'] = BandwidthRestrictionForm()
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_restriction.html', return_dict, context_instance=RequestContext(request))
        
@authentication_required
def create_restriction(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['rests'] = BandwidthRestriction.objects.all()
    
    if request.method == 'POST':
        forms_dict['restform'] = BandwidthRestrictionForm(request.POST)
        
        if forms_dict['restform'].is_valid():
            try:
                rest =  forms_dict['restform'].save()
                request.user.message_set.create(message="Restrição cadastrada com sucesso.")
                return HttpResponseRedirect("%s/restriction/new" % (request.META['SCRIPT_NAME']))
            except Exception:
                return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
                request.user.message_set.create(message="O limite de restrições cadastradas foi atingido e a restrição não foi adicionada.")
                return render_to_response('bkp/new_restriction.html', return_dict, context_instance=RequestContext(request))
        else:
            # Load forms and vars
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e a restrição não foi cadastrada.")
            return render_to_response('bkp/new_restriction.html', return_dict, context_instance=RequestContext(request))
        
    
### Password Management ###
@authentication_required
def new_password(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        forms_dict['pwdform'] = PasswordChangeForm(return_dict['current_user'])
        # Load forms and vars
        return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_password.html', return_dict, context_instance=RequestContext(request))

@authentication_required
def change_password(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['pwdform'] = PasswordChangeForm(return_dict['current_user'], request.POST)
        
        if forms_dict['pwdform'].is_valid():
            request.user.set_password(forms_dict['pwdform'].cleaned_data['new_password1'])
            request.user.save()
            request.user.message_set.create(message="Senha foi alterada com sucesso.")
            return __redirect_back_or_default(request, default=__root_path(request))
        else:
            # Load forms and vars
            request.user.message_set.create(message="Houve um erro e a senha não foi alterada.")
            return_dict = __merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/new_password.html', return_dict, context_instance=RequestContext(request))



###
###   Auxiliar Definitions
###


def __merge_dicts(main_dict, *dicts_list):
    """Merge one dict with a list of dicts."""
    for dict in dicts_list:
        main_dict.update(dict)
    return main_dict        

def __store_location(request):
    """Stores current user location"""
    request.session["location"] = request.build_absolute_uri()

def __redirect_back_or_default(request, default, except_pattern=None):
    """Redirects user back or to a given default place
    unless default place matches an except_pattern
    """
    if "location" in request.session:
        import re
        
        if except_pattern:
            if re.search(except_pattern,request.session["location"]):
                del(request.session["location"]) # use default location
        else:   
            # Try to find redirect error
            referer_full_path = request.META['HTTP_REFERER']
            request_path = request.META['PATH_INFO']
            slice_path_re = 'https?://(www\.)?[\w\d\-_ ]+?(:\d+)?(?P<short_path>/.*)'
            try: 
                referer_path = re.search(slice_path_re,referer_full_path).group('short_path')
                if re.search(referer_path, request_path):
                    del(request.session["location"]) # use default location
            except Exception:
                pass
    redirect = ("location" in request.session) and request.session["location"] or default
    return HttpResponseRedirect(redirect)


def __root_path(request):
    """Return root path."""
    return "%s/" % (request.META['SCRIPT_NAME'])
    
def __login_path(request):
    """Returns login path."""
    return "%s/session/new" % (request.META['SCRIPT_NAME'])

def __computer_path(request, computer_id):
    """Returns computer path."""
    return "%s/computer/%s" % (request.META['SCRIPT_NAME'],computer_id)

def __procedure_path(request, procedure_id, computer_id):
    """Returns procedure path."""
    return "%s/computer/%s/procedure/%s" % (request.META['SCRIPT_NAME'],computer_id,procedure_id)

def __schedule_path(request, schedule_id, procedure_id, computer_id):
    """Returns schedule path."""
    return "%s/computer/%s/procedure/%s/schedule/%s" % (request.META['SCRIPT_NAME'],computer_id,procedure_id,schedule_id)

def __edit_config_path(request):
    """Returns edit config path."""
    return "%s/config/edit" % (request.META['SCRIPT_NAME'])

def absolute_file_path(filename, rel_dir):
    """Return full path to a file from script file location and given directory."""
    root_dir = absolute_dir_path(rel_dir)
    return os.path.join(root_dir, filename)


def absolute_dir_path(rel_dir):
    """Return full path to a directory from script file location."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_dir)

def remove_or_leave(filepath):
    """Remove file if exists."""
    try:
        os.remove(filepath)
    except os.error:
        # Leave
        pass
