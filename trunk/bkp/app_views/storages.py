#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Storage
from backup_corporativo.bkp.forms import StorageForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


@authentication_required
def new_storage(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        # Load forms and vars
        forms_dict['storform'] = StorageForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new/new_storage.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_storage(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        forms_dict['storform'] = StorageForm(request.POST)
        forms_list = forms_dict.values()
        if all([form.is_valid() for form in forms_list]):
            storage = forms_dict['storform'].save()
            return HttpResponseRedirect(storage_path(request, storage.id))
        else:
            # Load forms and vars
            request.user.message_set.create(message="Existem erros e o storage não foi cadastrado.")
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
            return render_to_response('bkp/new/new_storage.html', return_dict, context_instance=RequestContext(request))

#        if temp_dict['compauxform'].cleaned_data['Procedure']:
#            forms_dict['procform'] = ProcedureForm(request.POST)
#        if temp_dict['compauxform'].cleaned_data['FileSet']:
#            forms_dict['fsetform'] = FileSetForm(request.POST)
#        if temp_dict['compauxform'].cleaned_data['Schedule']:
#            forms_dict['schedform'] = ScheduleForm(request.POST)
#        if temp_dict['compauxform'].cleaned_data['Trigger']:
#            if triggclass.lower() == 'weekly':
#                forms_dict['wtriggform'] = WeeklyTriggerForm(request.POST)
#                temp_dict['mtriggform'] = MonthlyTriggerForm()
#            elif triggclass.lower() == 'monthly':
#                temp_dict['wtriggform'] = WeeklyTriggerForm()
#                forms_dict['mtriggform'] = MonthlyTriggerForm(request.POST)
#        forms_list = forms_dict.values()
#        if all([form.is_valid() for form in forms_list]):
#            comp = forms_dict['compform'].save(commit=False)
#            proc = forms_dict['procform'].save(commit=False)
#            fset = forms_dict['fsetform'].save(commit=False)
#            sched = forms_dict['schedform'].save(commit=False)
#            trigg = forms_dict[triggform].save(commit=False)
#            comp.save()
#            comp.build_backup(proc, fset, sched, trigg)
#            request.user.message_set.create(message="Computador cadastrado com sucesso.")
#            return HttpResponseRedirect(computer_path(request, comp.id))
#        else:
#            # Load forms and vars
#            request.user.message_set.create(message="Existem erros e o computador não foi cadastrado.")
#            return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
#            return render_to_response('bkp/new/new_computer.html', return_dict, context_instance=RequestContext(request))
