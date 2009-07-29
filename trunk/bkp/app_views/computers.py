#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.forms import ComputerForm
from backup_corporativo.bkp.forms import ComputerAuxForm
from backup_corporativo.bkp.forms import ProcedureForm
from backup_corporativo.bkp.forms import MonthlyTriggerForm
from backup_corporativo.bkp.forms import WeeklyTriggerForm
from backup_corporativo.bkp.forms import FileSetForm
from backup_corporativo.bkp.forms import ScheduleForm
from backup_corporativo.bkp.forms import RestoreForm
from backup_corporativo.bkp.forms import HiddenRestoreForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


@authentication_required
def new_computer(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        # Load forms and vars
        forms_dict['compform'] = ComputerForm()
        forms_dict['procform'] = ProcedureForm()
        forms_dict['fsetform'] = FileSetForm()
        forms_dict['schedform'] = ScheduleForm()
        forms_dict['compauxform'] = ComputerAuxForm()
        forms_dict['mtriggform'] = MonthlyTriggerForm()
        forms_dict['wtriggform'] = WeeklyTriggerForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new/new_computer.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_computer(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        temp_dict['compauxform'] = ComputerAuxForm(request.POST)

        if temp_dict['compauxform'].is_valid():
            triggclass = temp_dict['compauxform'].cleaned_data['schedule_type']
            if triggclass == 'Weekly':
                triggform = 'wtriggform'
            elif triggclass == 'Monthly':
                triggform = 'mtriggform'
            else:
                raise Exception('Tipo de agendamento desconhecido ao adicionar computador.')
            
            forms_dict['compform'] = ComputerForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['Procedure']:
                forms_dict['procform'] = ProcedureForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['FileSet']:
                forms_dict['fsetform'] = FileSetForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['Schedule']:
                forms_dict['schedform'] = ScheduleForm(request.POST)
            if temp_dict['compauxform'].cleaned_data['Trigger']:
                if triggclass.lower() == 'weekly':
                    forms_dict['wtriggform'] = WeeklyTriggerForm(request.POST)
                    temp_dict['mtriggform'] = MonthlyTriggerForm()
                elif triggclass.lower() == 'monthly':
                    temp_dict['wtriggform'] = WeeklyTriggerForm()
                    forms_dict['mtriggform'] = MonthlyTriggerForm(request.POST)
            forms_list = forms_dict.values()
            if all([form.is_valid() for form in forms_list]):
                comp = forms_dict['compform'].save(commit=False)
                proc = forms_dict['procform'].save(commit=False)
                fset = forms_dict['fsetform'].save(commit=False)
                sched = forms_dict['schedform'].save(commit=False)
                trigg = forms_dict[triggform].save(commit=False)
                comp.save()
                comp.build_backup(proc, fset, sched, trigg)
                request.user.message_set.create(message="Computador cadastrado com sucesso.")
                return HttpResponseRedirect(computer_path(request, comp.id))
            else:
                # Load forms and vars
                request.user.message_set.create(message="Existem erros e o computador não foi cadastrado.")
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
                return render_to_response('bkp/new/new_computer.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def edit_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    comp = get_object_or_404(Computer, pk=computer_id)
    vars_dict['comp'] = comp

    if request.method == 'GET': # Edit computer
        forms_dict['compform'] = ComputerForm(instance=comp)
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit/edit_computer.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def update_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    comp = get_object_or_404(Computer, pk=computer_id)
    vars_dict['comp'] = comp

    if request.method == 'POST':
        forms_dict['compform'] = ComputerForm(request.POST,instance=comp)
        
        if forms_dict['compform'].is_valid():
            forms_dict['compform'].save()
            request.user.message_set.create(message="Computador foi alterado com sucesso.")
            return HttpResponseRedirect(computer_path(request, computer_id))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o computador não foi alterado.")
            return render_to_response('bkp/edit/edit_computer.html', return_dict, context_instance=RequestContext(request))   


@authentication_required
def view_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    store_location(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer,pk=computer_id)
        vars_dict['procs'] = vars_dict['comp'].procedure_set.all()
        vars_dict['running_jobs'] = vars_dict['comp'].running_jobs()
        vars_dict['last_jobs'] = vars_dict['comp'].last_jobs()
        from backup_corporativo.bkp.bacula import Bacula
        vars_dict['compstatus'] = vars_dict['comp'].get_status()
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view/view_computer.html', return_dict, context_instance=RequestContext(request))    


@authentication_required
def delete_computer(request, computer_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['comp'] = get_object_or_404(Computer,pk=computer_id)
        request.user.message_set.create(message="Confirme a remoção do computador.")
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/delete/delete_computer.html', return_dict, context_instance=RequestContext(request))    
        
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.delete()
        request.user.message_set.create(message="Computador removido permanentemente.")            
        return redirect_back_or_default(request, default=root_path(request))  

### Job Restore ###
@authentication_required
def do_restore(request, computer_id):
    if request.method == 'POST':
        vars_dict, forms_dict, return_dict = global_vars(request)    
        forms_dict['restore_form'] = RestoreForm(request.POST)
        forms_dict['hidden_restore_form'] = HiddenRestoreForm(request.POST)
        forms_list = forms_dict.values()

        if all([form.is_valid() for form in forms_list]):
            fileset_name = forms_dict['hidden_restore_form'].cleaned_data['fileset_name']
            target_dt = forms_dict['hidden_restore_form'].cleaned_data['target_dt']
            src_client = forms_dict['hidden_restore_form'].cleaned_data['client_source']
            client_restore = forms_dict['restore_form'].cleaned_data['client_restore']
            restore_path = forms_dict['restore_form'].cleaned_data['restore_path']
            from backup_corporativo.bkp.bacula import Bacula
            Bacula.run_restore(ClientName=src_client, Date=target_dt, ClientRestore=client_restore, Where=restore_path, fileset_name=fileset_name)
            request.user.message_set.create(message="Uma requisição de restauração foi enviada para ser executado no computador.")
            return HttpResponseRedirect(computer_path(request, computer_id))
        else:
            vars_dict['comp_id'] = computer_id
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/new/new_restore.html', return_dict, context_instance=RequestContext(request))


def new_restore(request, computer_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        if not 'fset' in request.GET:
            raise Exception('JobID parameter is missing.')
        if not 'dt' in request.GET:
            raise Exception('Date parameter is missing.')
        if not 'src' in request.GET:
            raise Exception('ClientName parameter is missing.')

        vars_dict['src_client'] = request.GET['src']
        vars_dict['target_dt'] = request.GET['dt']
        vars_dict['fileset_name'] = request.GET['fset']
        vars_dict['comp_id'] = computer_id
        forms_dict['restore_form'] = RestoreForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new/new_restore.html', return_dict, context_instance=RequestContext(request))
        
def test_computer(request, computer_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.run_test_job()
        request.user.message_set.create(message="Uma requisição teste foi enviada para ser executado no computador.")
        return HttpResponseRedirect(computer_path(request, computer_id))
        

# TODO remove code from view, move it to models.py
# Tratar criptografia opcional.
# Futuramente: tratar porta do cliente
# Futuramente: tratar diretório de configuração do bacula
def generate_storage_dump_file(computer):
    "generate file deamon config file"
    fd_dict =   {'Name': computer.computer_name, 
                'FDport':'9102',
                'WorkingDirectory':'/var/bacula/working ',
                'Pid Directory':'/var/run ',
#                'WorkingDirectory':'C:\\Documents and Settings\\All Users\\Dados de aplicativos\\Bacula\\Work'
#                'Pid Directory':'C:\\Documents and Settings\\All Users\\Dados de aplicativos\\Bacula\\Work'
                'Maximum Concurrent Jobs':'5',
                'PKI Signatures':'Yes',
                'PKI Encryption':'Yes',
                'PKI Keypair':'/etc/bacula/fd-example.pem',
                'PKI Master Key':'/etc/bacula/master.cert',
                }
    dir_dict =  {'Name':'devel-dir',
                'Password':'T9gi7y1BoRoR1eZekT4o',
                }
    msg_dict =  {'Name':'Standard',
                'director':'devel-dir = all, !skipped, !restored',
                }
    dump = []

    dump.append("#\n")
    dump.append("# Generated by Nimbus\n") #TODO: Add nimbus version and timestamp here
    dump.append("#\n")
    dump.append("FileDaemon {\n")
    for k in fd_dict.keys():
        dump.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':fd_dict[k]})
    dump.append("}\n\n")
    dump.append("Director {\n")
    for k in dir_dict.keys():
        dump.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dir_dict[k]})
    dump.append("}\n\n")
    dump.append("Messages {\n")
    for k in msg_dict.keys():
        dump.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':msg_dict[k]})
    dump.append("}\n\n")
    
    return ''.join(dump)


@authentication_required
def client_config_dump(request, computer_id):
    """Generates and provides download to a file deamon client config file."""
    if request.method == 'GET':
        computer = Computer.objects.get(pk=computer_id)
        dump_file = generate_storage_dump_file(computer)
        
    	# Return file for download
        response = HttpResponse(mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=bacula-sd.conf'
        response.write(dump_file)
        return response
