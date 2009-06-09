#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO:
# Falta tratar erros URL caso o ID esteja faltando 
# Criar erro caso ID na URL seja de um computador que nao existe
# Falta customizar erros
# Validar gatilho c/ tipo de agendamento

# Models
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.models import WeeklyTrigger
from backup_corporativo.bkp.models import MonthlyTrigger
from backup_corporativo.bkp.models import UniqueTrigger
from backup_corporativo.bkp.models import FileSet
# Forms
from backup_corporativo.bkp.forms import ComputerForm
from backup_corporativo.bkp.forms import ProcedureForm
from backup_corporativo.bkp.forms import ScheduleForm
from backup_corporativo.bkp.forms import WeeklyTriggerForm
from backup_corporativo.bkp.forms import MonthlyTriggerForm
from backup_corporativo.bkp.forms import UniqueTriggerForm
from backup_corporativo.bkp.forms import FileSetForm
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


###
###   Views
###


def index(request):
    __store_location(request)
    return render_to_response('bkp/index.html', {'script_name':request.META['SCRIPT_NAME']})

### Computers ###

def list_computers(request):
    comps = Computer.objects.all()
    compform = ComputerForm()
    return render_to_response('bkp/list_computers.html', {'script_name':request.META['SCRIPT_NAME'],'comps':comps,'compform':compform})


def edit_computer(request, computer_id):
    comp = get_object_or_404(Computer, pk=computer_id)
    if request.method == 'GET': # Edit computer
        compform = ComputerForm(instance=comp)
        return render_to_response('bkp/edit_computer.html', {'script_name':request.META['SCRIPT_NAME'],'comp':comp,'compform': compform,})
    elif request.method == 'POST': # Update computer
        compform = ComputerForm(request.POST,instance=comp)
        if compform.is_valid():
            compform.save()
            return HttpResponseRedirect("%(script_name)s/computer/%(id)i" % {'script_name':request.META['SCRIPT_NAME'],'id':comp.id})
        else:   # Update failed re-render
            return render_to_response('bkp/edit_computer.html', {'script_name':request.META['SCRIPT_NAME'],'comp':comp,'compform': compform,})
            
def view_computer(request, computer_id):
    __store_location(request)
    if request.method == 'GET':  # View computer
        comp = get_object_or_404(Computer,pk=computer_id)
        compform = ComputerForm()
        comps = Computer.objects.all()
        procs = comp.procedures_list()
        procform = ProcedureForm() # An unbound form
        return render_to_response('bkp/view_computer.html', {'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procs':procs,'procform':procform})

    
def delete_computer(request, computer_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=computer_id)
        comp.delete()
        except_pattern = "computer/%s" % (computer_id)
        default = "%(script_name)s/" % {'script_name':request.META['SCRIPT_NAME'],}
        return __redirect_back_or_default(request, default, except_pattern)


def create_computer(request):
    if request.method == 'POST':  # If the form has been submitted...
            compform = ComputerForm(request.POST)
            if compform.is_valid():
                computer = compform.save()
                computer.generate_password()
                return HttpResponseRedirect("%(script_name)s/computer/%(id)i" % {'script_name':request.META['SCRIPT_NAME'],'id':computer.id})
            else:
                comps = Computer.objects.all()           
                return render_to_response('bkp/list_computers.html', {'script_name':request.META['SCRIPT_NAME'],'comps':comps,'compform':compform})

### Procedure ###

def edit_procedure(request, computer_id, procedure_id):
    comp = get_object_or_404(Computer, pk=computer_id)
    proc = get_object_or_404(Procedure, pk=procedure_id)
    if request.method == 'GET': # Edit computer
        procform = ProcedureForm(instance=proc)
        return render_to_response('bkp/edit_procedure.html', {'script_name':request.META['SCRIPT_NAME'],'comp':comp,'proc':proc,'procform': procform,})
    elif request.method == 'POST': # Update procedure
        procform = ProcedureForm(request.POST,instance=proc)
        import pdb;pdb.set_trace()
        if procform.is_valid():

            procform.save()
            return HttpResponseRedirect("%(script_name)s/computer/%(comp_id)i/procedure/%(proc_id)i" % {'script_name':request.META['SCRIPT_NAME'],'comp_id':comp.id,'proc_id':proc.id})
        else:   # Update failed re-render
            return render_to_response('bkp/edit_procedure.html', {'script_name':request.META['SCRIPT_NAME'],'comp':comp,'proc':proc,'procform': procform,})


def view_procedure(request, computer_id, procedure_id):
    __store_location(request)
    if request.method == 'GET':
        if procedure_id:
            comp = get_object_or_404(Computer, pk=computer_id)
            compform = ComputerForm()
            comps = Computer.objects.all()
            proc = get_object_or_404(Procedure, pk=procedure_id)
            procform = ProcedureForm()
            procs = comp.procedures_list()
            fsets = proc.filesets_list()
            fsetform = FileSetForm() # An unbound form
            scheds = proc.schedules_list()
            schedform = ScheduleForm() # An unbound form
            return render_to_response('bkp/view_procedure.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'schedform':schedform})
        else:
            return HttpResponseRedirect("%(script_name)s/computer/%(computer_id)i", {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id})

    
def create_procedure(request, computer_id):
    if request.method == 'POST': # If the form has been submitted...
        procform = ProcedureForm(request.POST)
        if procform.is_valid():
            procedure = Procedure()
            procedure.computer_id = computer_id
            procedure.procedure_name = procform.cleaned_data['procedure_name']
            procedure.restore_path = procform.cleaned_data['restore_path']
            procedure.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure.id})
        else:
            comp = get_object_or_404(Computer, pk=computer_id)
            compform = ComputerForm()
            comps = Computer.objects.all()
            procs = comp.procedures_list()
            return render_to_response('bkp/view_computer.html', {'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procs':procs,'procform':procform})


def delete_procedure(request, computer_id, procedure_id):
    if request.method == 'POST':
        proc = get_object_or_404(Procedure, pk=procedure_id)
        proc.delete()
        except_pattern = "procedure/%s" % (procedure_id)
        default = "%(script_name)s/computer/%(computer_id)s" % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,}
        return __redirect_back_or_default(request, default, except_pattern)




### Schedule ###

def view_schedule(request, computer_id, procedure_id, schedule_id):
    __store_location(request)
    if request.method == 'GET':
        comp = get_object_or_404(Computer, pk=computer_id)
        comps = Computer.objects.all()
        compform = ComputerForm()
        proc = get_object_or_404(Procedure, pk=procedure_id)
        procs = Procedure.objects.filter(computer=comp)
        procform = ProcedureForm()
        sched = get_object_or_404(Schedule, pk=schedule_id)
        sched_lower_type = sched.type.lower()
        scheds = Schedule.objects.filter(procedure=proc)
        fsets = proc.filesets_list()
        fsetform = FileSetForm() # An unbound form
        schedform = ScheduleForm() # An unbound form
        if (sched.type == 'Weekly'):
            try:
                trigger = WeeklyTrigger.objects.get(schedule=sched)
                triggerform = WeeklyTriggerForm(instance=trigger)
                triggerformempty = False
            except WeeklyTrigger.DoesNotExist:
                triggerform = WeeklyTriggerForm()
                triggerformempty = True
        elif (sched.type == 'Monthly'):
            try:
                trigger = MonthlyTrigger.objects.get(schedule=sched)
                triggerform = MonthlyTriggerForm(instance=trigger)                
                triggerformempty = False
            except MonthlyTrigger.DoesNotExist:
                triggerform = MonthlyTriggerForm()
                triggerformempty = True
        elif (sched.type == 'Unique'):
            try:
                trigger = UniqueTrigger.objects.get(schedule=sched)
                triggerform = UniqueTriggerForm(instance=trigger)
                triggerformempty = False
            except UniqueTrigger.DoesNotExist:
                triggerform = UniqueTriggerForm()
                triggerformempty = True
        return render_to_response('bkp/view_schedule.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'sched':sched,'schedform':schedform,'triggerform':triggerform,'triggerformempty':triggerformempty,'sched_lower_type':sched_lower_type,})


def create_schedule(request, computer_id, procedure_id):
    if request.method == 'POST': # If the form has been submitted...
        schedform = ScheduleForm(request.POST)
        if schedform.is_valid():
            schedule = Schedule()
            schedule.procedure_id = procedure_id
            schedule.type = schedform.cleaned_data['type']
            schedule.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule.id})
        else:
            comp = get_object_or_404(Computer, pk=computer_id)
            compform = ComputerForm()
            comps = Computer.objects.all()
            proc = get_object_or_404(Procedure, pk=procedure_id)
            procform = ProcedureForm()
            procs = comp.procedures_list()
            fsets = proc.filesets_list()
            fsetform = FileSetForm() # An unbound form            
            scheds = proc.schedules_list()

            return render_to_response('bkp/view_procedure.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'schedform':schedform})


def delete_schedule(request, computer_id, procedure_id, schedule_id):
    if request.method == 'POST': # If the form has been submitted...
        sched = get_object_or_404(Schedule, pk=schedule_id)
        sched.delete()
        except_pattern = "schedule/%s" % (schedule_id)
        default = '%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,}
        return __redirect_back_or_default(request, default, except_pattern)

        
        
### Triggers ###

def weeklytrigger(request, computer_id, procedure_id, schedule_id):
    if request.method == 'POST': # If the form has been submitted...
        sched = get_object_or_404(Schedule, pk=schedule_id)
        triggerform = WeeklyTriggerForm(request.POST)
        if triggerform.is_valid():
            try:
                wtrigger = WeeklyTrigger.objects.get(schedule=sched)
            except WeeklyTrigger.DoesNotExist:
                wtrigger = WeeklyTrigger()
            wtrigger.schedule_id = schedule_id
            wtrigger.sunday = triggerform.cleaned_data['sunday']
            wtrigger.monday = triggerform.cleaned_data['monday']
            wtrigger.tuesday = triggerform.cleaned_data['tuesday']
            wtrigger.wednesday = triggerform.cleaned_data['wednesday']
            wtrigger.thursday = triggerform.cleaned_data['thursday']
            wtrigger.friday = triggerform.cleaned_data['friday']
            wtrigger.saturday = triggerform.cleaned_data['saturday']
            wtrigger.hour = triggerform.cleaned_data['hour']
            wtrigger.level = triggerform.cleaned_data['level']
            wtrigger.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule_id})
        else:
            comp = get_object_or_404(Computer, pk=computer_id)
            comps = Computer.objects.all()
            compform = ComputerForm()
            proc = get_object_or_404(Procedure, pk=procedure_id)
            procs = Procedure.objects.filter(computer=comp)
            procform = ProcedureForm()
            sched = get_object_or_404(Schedule, pk=schedule_id)
            sched_lower_type = sched.type.lower()
            scheds = Schedule.objects.filter(procedure=proc)
            fsets = proc.filesets_list()
            fsetform = FileSetForm() # An unbound form
            schedform = ScheduleForm() # An unbound form
            triggerformempty = True
        
            return render_to_response('bkp/view_schedule.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'sched':sched,'schedform':schedform,'triggerform':triggerform,'triggerformempty':triggerformempty,'sched_lower_type':sched_lower_type,})        


def monthlytrigger(request, computer_id, procedure_id, schedule_id):
    sched = get_object_or_404(Schedule, pk=schedule_id)
    if request.method == 'POST': # If the form has been submitted...
        triggerform = MonthlyTriggerForm(request.POST)
        if triggerform.is_valid():
            try:
                mtrigger = MonthlyTrigger.objects.get(schedule=sched)
            except MonthlyTrigger.DoesNotExist:
                mtrigger = MonthlyTrigger()
            mtrigger.schedule_id = schedule_id
            mtrigger.hour = triggerform.cleaned_data['hour']
            mtrigger.level = triggerform.cleaned_data['level']
            mtrigger.target_days = triggerform.cleaned_data['target_days']
            mtrigger.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule_id})
        else:
            comp = get_object_or_404(Computer, pk=computer_id)
            comps = Computer.objects.all()
            compform = ComputerForm()
            proc = get_object_or_404(Procedure, pk=procedure_id)
            procs = Procedure.objects.filter(computer=comp)
            procform = ProcedureForm()
            sched_lower_type = sched.type.lower()
            scheds = Schedule.objects.filter(procedure=proc)
            fsets = proc.filesets_list()
            fsetform = FileSetForm() # An unbound form
            schedform = ScheduleForm() # An unbound form
            triggerformempty = True
            return render_to_response('bkp/view_schedule.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'sched':sched,'schedform':schedform,'triggerform':triggerform,'triggerformempty':triggerformempty,'sched_lower_type':sched_lower_type,})        

            
def uniquetrigger(request, computer_id, procedure_id, schedule_id):
    sched = get_object_or_404(Schedule, pk=schedule_id)
    if request.method == 'POST': # If the form has been submitted...
        triggerform = UniqueTriggerForm(request.POST)
        if triggerform.is_valid():
            try:
                utrigger = UniqueTrigger.objects.get(schedule=sched)
            except UniqueTrigger.DoesNotExist:
                utrigger = UniqueTrigger()
            utrigger.schedule_id = schedule_id
            utrigger.target_date = triggerform.cleaned_data['target_date']
            utrigger.hour = triggerform.cleaned_data['hour']
            utrigger.level = triggerform.cleaned_data['level']
            utrigger.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule_id})
        else:
            comp = get_object_or_404(Computer, pk=computer_id)
            comps = Computer.objects.all()
            compform = ComputerForm()
            proc = get_object_or_404(Procedure, pk=procedure_id)
            procs = Procedure.objects.filter(computer=comp)
            procform = ProcedureForm()
            sched_lower_type = sched.type.lower()
            scheds = Schedule.objects.filter(procedure=proc)
            fsets = proc.filesets_list()
            fsetform = FileSetForm() # An unbound form
            schedform = ScheduleForm() # An unbound form
            triggerformempty = True      
            
            return render_to_response('bkp/view_schedule.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'sched':sched,'schedform':schedform,'triggerform':triggerform,'triggerformempty':triggerformempty,'sched_lower_type':sched_lower_type,})        
        
        
### FileSets ###

def create_fileset(request, computer_id, procedure_id):
    if request.method == 'POST': # If the form has been submitted...
        fsetform = FileSetForm(request.POST)
        if fsetform.is_valid():
            fileset = FileSet()
            fileset.procedure_id = procedure_id
            fileset.path = fsetform.cleaned_data['path']
            fileset.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id})
        else:
            comp = get_object_or_404(Computer, pk=computer_id)
            compform = ComputerForm()
            comps = Computer.objects.all()
            proc = get_object_or_404(Procedure, pk=procedure_id)
            procform = ProcedureForm()
            procs = comp.procedures_list()
            fsets = proc.filesets_list()
            scheds = proc.schedules_list()
            schedform = ScheduleForm() # An unbound form

            return render_to_response('bkp/view_procedure.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'schedform':schedform})

def delete_fileset(request, computer_id, procedure_id, fileset_id):
    if request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fileset_id)
        fset.delete()
        default = '%(script_name)s/computer/%(comp_id)s/procedure/%(proc_id)s' % {'script_name':request.META['SCRIPT_NAME'],'comp_id':computer_id,'proc_id':procedure_id}
        return __redirect_back_or_default(request, default)


        
###
###   Auxiliar Definitions
###

def __store_location(request):
    request.session["location"] = request.build_absolute_uri()

def __redirect_back_or_default(request, default, except_pattern=None):
    if except_pattern and ("location" in request.session):
        import re
        if re.search(except_pattern,request.session["location"]):
            del(request.session["location"]) # use default location
    
    redirect = ("location" in request.session) and request.session["location"] or default
    return HttpResponseRedirect(redirect)