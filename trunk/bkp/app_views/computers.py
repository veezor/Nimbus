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
            job_id = forms_dict['hidden_restore_form'].cleaned_data['job_id']
            target_dt = forms_dict['hidden_restore_form'].cleaned_data['target_dt']
            src_client = forms_dict['hidden_restore_form'].cleaned_data['client_source']
            client_restore = forms_dict['restore_form'].cleaned_data['client_restore']
            restore_path = forms_dict['restore_form'].cleaned_data['restore_path']
            from backup_corporativo.bkp.bacula import Bacula
            Bacula.run_restore(ClientName=src_client, JobId=job_id, Date=target_dt, ClientRestore=client_restore, Where=restore_path)
            return HttpResponse('Pode restaurar!')
        else:
            vars_dict['comp_id'] = computer_id
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/new/new_restore.html', return_dict, context_instance=RequestContext(request))


def new_restore(request, computer_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        if not 'jid' in request.GET:
            raise Exception('JobID parameter is missing.')
        if not 'dt' in request.GET:
            raise Exception('Date parameter is missing.')
        if not 'src' in request.GET:
            raise Exception('ClientName parameter is missing.')

        vars_dict['src_client'] = request.GET['src']
        vars_dict['target_dt'] = request.GET['dt']
        vars_dict['job_id'] = request.GET['jid']
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
