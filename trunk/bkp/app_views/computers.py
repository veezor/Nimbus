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
        forms_dict['compauxform'] = ComputerAuxForm()
        forms_dict['mtriggform'] = MonthlyTriggerForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_computer.html', return_dict, context_instance=RequestContext(request))


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
                import pdb; pdb.set_trace()
                comp.save()
                comp.build_backup(proc, fset, sched, trigg)
                request.user.message_set.create(message="Computador cadastrado com sucesso.")
                return HttpResponseRedirect(computer_path(request, comp.id))
            else:
                # Load forms and vars
                request.user.message_set.create(message="Existem erros e o computador não foi cadastrado.")
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
                return render_to_response('bkp/new_computer.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def edit_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    comp = get_object_or_404(Computer, pk=computer_id)
    if request.method == 'GET': # Edit computer
        forms_dict['compform'] = ComputerForm(instance=comp)
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit_computer.html', return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['compform'] = ComputerForm(request.POST,instance=comp)
        
        if forms_dict['compform'].is_valid():
            forms_dict['compform'].save()
            request.user.message_set.create(message="Computador foi alterado com sucesso.")
            return HttpResponseRedirect(computer_path(request, comp.id))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o computador não foi alterado.")
            return render_to_response('bkp/edit_computer.html', return_dict, context_instance=RequestContext(request))   


@authentication_required
def view_computer(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    store_location(request)
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
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view_computer.html', return_dict, context_instance=RequestContext(request))    


@authentication_required
def delete_computer(request, computer_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.delete()
        request.user.message_set.create(message="Computador removido permanentemente.")            
        return redirect_back_or_default(request, default=root_path(request))  

### Job Restore ###
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
            redirect_back_or_default(request,root_path(request))
    
        return HttpResponse("restaura aí, vai!")


