#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import GlobalConfig
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
    vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    vars_dict['restore_prefix'] = "/computer/%s" % vars_dict['comp'].id

    if request.method == 'GET': # Edit computer
        forms_dict['compform'] = ComputerForm(instance=vars_dict['comp'])
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
        vars_dict['restore_prefix'] = "/computer/%s" % vars_dict['comp'].id
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
        vars_dict['restore_prefix'] = "/computer/%s" % comp.id
        request.user.message_set.create(message="Confirme a remoção do computador.")
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/delete/delete_computer.html', return_dict, context_instance=RequestContext(request))    
        
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.delete()
        request.user.message_set.create(message="Computador removido permanentemente.")            
        return redirect_back_or_default(request, default=root_path(request))  


        
def test_computer(request, computer_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.run_test_job()
        request.user.message_set.create(message="Uma requisição teste foi enviada para ser executado no computador.")
        return HttpResponseRedirect(computer_path(request, computer_id))
        

# TODO remove code from view, move it to models.py
def generate_storage_dump_file(computer):
    """Gera arquivo de configuraçãodo cliente bacula-sd.conf."""
    import time
    
    fd_dict =   {'Name': computer.computer_name, 
                'FDport':'9102', #TODO: tratar porta do cliente
                'Maximum Concurrent Jobs':'5',}
                
    if computer.computer_encryption:
        if computer.computer_so == 'UNIX':
            fd_dict.update( {'PKI Signatures':'Yes',
                            'PKI Encryption':'Yes',
                            'PKI Keypair':"""'/etc/bacula/%s'""" % (computer.computer_pem()),
                            'PKI Master Key':"""'/etc/bacula/master.cert'""",})
        elif computer.computer_so == 'WIN':
            fd_dict.update( {'PKI Signatures':'Yes',
                            'PKI Encryption':'Yes',
                            'PKI Keypair':"""'C:\\Documents and Settings\\All Users\\Dados de aplicativos\\Bacula\\Work\\%s'""" % (computer.computer_pem()),
                            'PKI Master Key':"""'C:\\Documents and Settings\\All Users\\Dados de aplicativos\\Bacula\\Work\\master.cert'""",})
        
    if computer.computer_so == 'UNIX':
        fd_dict.update( {'WorkingDirectory':'/var/bacula/working ',
                        'Pid Directory':'/var/run ',})
    elif computer.computer_so == 'WIN':
        fd_dict.update( {'WorkingDirectory':"""'C:\\Documents and Settings\\All Users\\Dados de aplicativos\\Bacula\\Work'""",
                        'Pid Directory':"""'C:\\Documents and Settings\\All Users\\Dados de aplicativos\\Bacula\\Work'""",})

    gconf = GlobalConfig.objects.get(pk=1)
    
    dir_dict =  {'Name':gconf.bacula_name,
                'Password':"""'%s'""" % (gconf.director_password),
                }
    msg_dict =  {'Name':'Standard',
                'director':'devel-dir = all, !skipped, !restored',
                }
    dump = []

    dump.append("#\n")
    # TODO adicionar version stamp aqui
    dump.append("# Generated by Nimbus %s\n" % (time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())))
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
        
        
@authentication_required
def client_pem_dump(request, computer_id):
    """Generates and provides download to a file deamon client config file."""
    if request.method == 'GET':
        computer = Computer.objects.get(pk=computer_id)
        dump_file = computer.dump_pem()
        
    	# Return file for download
        response = HttpResponse(mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s'% (computer.computer_pem())
        response.write(dump_file)
        return response

