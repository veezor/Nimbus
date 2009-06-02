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


def index(request):
    return render_to_response('bkp/index.html', {'script_name':request.META['SCRIPT_NAME']})

# Computers 
def list_computers(request):
    comps = Computer.objects.all()
    compform = ComputerForm()
    return render_to_response('bkp/list_computers.html', {'script_name':request.META['SCRIPT_NAME'],'comps':comps,'compform':compform})


def add_computer(request):
    form = ComputerForm() # An unbound form
    return render_to_response('bkp/add_computer.html', {'script_name':request.META['SCRIPT_NAME'],'form': form,})


def edit_computer(request, computer_id=None):
    if request.method == 'GET': # Edit computer
        try:
            comp = Computer.objects.get(pk=computer_id)
        except Computer.DoesNotExist:
            return HttpResponse('Erro de URL. Computador Nao Existe (Falta customizar mensagem de erro)')
        form = ComputerForm(instance=comp) # An unbound form
        return render_to_response('bkp/edit_computer.html', {'script_name':request.META['SCRIPT_NAME'],'comp':comp,'form': form,})
    elif request.method == 'POST': # Update computer
        form = ComputerForm(request.POST)
        if form.is_valid():
            try:
                comp = Computer.objects.get(pk=computer_id)
            except Computer.DoesNotExist:
                return HttpResponse('Erro de URL. Computador Nao Existe (Falta customizar mensagem de erro)')
            comp.name = form.cleaned_data['name']
            comp.ip = form.cleaned_data['ip']
            comp.description = form.cleaned_data['description']
            comp.save()
            return HttpResponseRedirect("%(script_name)s/computer/%(id)i" % {'script_name':request.META['SCRIPT_NAME'],'id':comp.id})
        else:
            return HttpResponse('Erro de formulario (falta customizar erro)')
    else: 
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})        
            
def view_computer(request, computer_id=None):
    if request.method == 'GET':  # View computer
        if computer_id:
            try:
                comp = Computer.objects.get(pk=computer_id)
            except Computer.DoesNotExist:
                return HttpResponse('Erro de URL. Computador Nao Existe (Falta customizar mensagem de erro)')
            compform = ComputerForm()
            comps = Computer.objects.all()
            procs = comp.procedures_list()
            procform = ProcedureForm() # An unbound form
            return render_to_response('bkp/view_computer.html', {'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procs':procs,'procform':procform})
        else:
            return HttpResponse('Erro de URL. Falta ID do computador (Falta customizar mensagem de erro)')
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    

def delete_computer(request, computer_id=None):
    if request.method == 'POST':
        try:
            comp = Computer.objects.get(pk=computer_id)
        except Computer.DoesNotExist:
            return HttpResponse('Erro de URL. Computador Nao Existe (Falta customizar mensagem de erro)')
        comp.delete()
        return HttpResponseRedirect("%(script_name)s/computers/" % {'script_name':request.META['SCRIPT_NAME'],})
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    

def create_computer(request):
    if request.method == 'POST':  # If the form has been submitted...
            form = ComputerForm(request.POST)
            if form.is_valid():
                computer = form.save()
                return HttpResponseRedirect("%(script_name)s/computer/%(id)i" % {'script_name':request.META['SCRIPT_NAME'],'id':computer.id})
            else:
                return HttpResponse('Erro de Formulario (Falta customizar mensagem de erro)')
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    


# Procedure
def view_procedure(request, computer_id=None, procedure_id=None):
    if request.method == 'GET':
        if procedure_id:
            try: 
                proc = Procedure.objects.get(pk=procedure_id)
            except Computer.DoesNotExist:
                return HttpResponse('Erro de URL. Procedimento Nao Existe (Falta customizar mensagem de erro)')
            comp = Computer.objects.get(pk=computer_id)
            compform = ComputerForm()
            comps = Computer.objects.all()
            procform = ProcedureForm()
            procs = comp.procedures_list()
            fsets = proc.filesets_list()
            fsetform = FileSetForm() # An unbound form
            scheds = proc.schedules_list()
            schedform = ScheduleForm() # An unbound form
            return render_to_response('bkp/view_procedure.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'schedform':schedform})
        else:
            return HttpResponse('Erro de URL. Falta id do procedimento na url (Falta customizar mensagem de erro)')
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    


def create_procedure(request, computer_id=None):
    if request.method == 'POST': # If the form has been submitted...
        form = ProcedureForm(request.POST)
        if form.is_valid():
            procedure = Procedure()
            procedure.computer_id = computer_id
            procedure.name = form.cleaned_data['name']
            procedure.restore_path = form.cleaned_data['restore_path']
            procedure.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure.id})
        else:
            return HttpResponse("Erro de Formulario (Falta customizar mensagem de erro)")
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    

def delete_procedure(request, computer_id=None, procedure_id=None):
    if request.method == 'POST':
        try:
            proc = Procedure.objects.get(pk=procedure_id)
        except Procedure.DoesNotExist:
            return HttpResponse('Erro de URL. Procedumento nao existe.')
        proc.delete()
        return HttpResponseRedirect('%(script_name)s/computer/%(comp_id)s' % {'script_name':request.META['SCRIPT_NAME'],'comp_id':computer_id})
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    



# Schedule
def view_schedule(request, computer_id=None, procedure_id=None, schedule_id=None):
    if request.method == 'GET':
        if schedule_id:
            comp = Computer.objects.get(pk=computer_id)
            comps = Computer.objects.all()
            compform = ComputerForm()
            proc = Procedure.objects.get(pk=procedure_id)
            procs = Procedure.objects.filter(computer=comp)
            procform = ProcedureForm()
            sched = Schedule.objects.get(pk=schedule_id)
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
            return render_to_response('bkp/view_schedule.html',{'script_name':request.META['SCRIPT_NAME'],'compform':compform,'comps':comps,'comp':comp,'procform':procform,'procs':procs,'proc':proc,'fsets':fsets,'fsetform':fsetform,'scheds':scheds,'sched':sched,'schedform':schedform,'triggerform':triggerform,'triggerformempty':triggerformempty,'sched_lower_type':sched_lower_type})
        else:
            return HttpResponse('Erro de URL. Falta id do agendamento na url (Falta customizar mensagem de erro)')
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    

def create_schedule(request, computer_id=None, procedure_id=None):
    if request.method == 'POST': # If the form has been submitted...
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = Schedule()
            schedule.procedure_id = procedure_id
            schedule.type = form.cleaned_data['type']
            schedule.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule.id})
        else:
            return HttpResponse("Erro de Formulario (Falta customizar mensagem de erro)")
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    


def delete_schedule(request, computer_id=None, procedure_id=None, schedule_id=None):
    if request.method == 'POST': # If the form has been submitted...
        sched = Schedule.objects.get(pk=schedule_id)
        sched.delete()
        return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,})
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    
        
        
# Triggers        

def weeklytrigger(request, computer_id=None, procedure_id=None, schedule_id=None):
    if request.method == 'POST': # If the form has been submitted...
        form = WeeklyTriggerForm(request.POST)
        if form.is_valid():
            try:
                sched = Schedule.objects.get(pk=schedule_id)
                wtrigger = WeeklyTrigger.objects.get(schedule=sched)
            except WeeklyTrigger.DoesNotExist:
                wtrigger = WeeklyTrigger()
            wtrigger.schedule_id = schedule_id
            wtrigger.sunday = form.cleaned_data['sunday']
            wtrigger.monday = form.cleaned_data['monday']
            wtrigger.tuesday = form.cleaned_data['tuesday']
            wtrigger.wednesday = form.cleaned_data['wednesday']
            wtrigger.thursday = form.cleaned_data['thursday']
            wtrigger.friday = form.cleaned_data['friday']
            wtrigger.saturday = form.cleaned_data['saturday']
            wtrigger.hour = form.cleaned_data['hour']
            wtrigger.level = form.cleaned_data['level']
            wtrigger.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule_id})
        else:
            return HttpResponse("Erro de Formulario (Falta customizar mensagem de erro)")
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    


def monthlytrigger(request, computer_id=None, procedure_id=None, schedule_id=None):
    if request.method == 'POST': # If the form has been submitted...
        form = MonthlyTriggerForm(request.POST)
        if form.is_valid():
            try:
                sched = Schedule.objects.get(pk=schedule_id)
                mtrigger = MonthlyTrigger.objects.get(schedule=sched)
            except MonthlyTrigger.DoesNotExist:
                mtrigger = MonthlyTrigger()
            mtrigger.schedule_id = schedule_id
            mtrigger.hour = form.cleaned_data['hour']
            mtrigger.level = form.cleaned_data['level']
            mtrigger.target_days = form.cleaned_data['target_days']
            mtrigger.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule_id})
        else:
            return HttpResponse("Erro de Formulario (Falta customizar mensagem de erro)")
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    
            
def uniquetrigger(request, computer_id=None, procedure_id=None, schedule_id=None):
    if request.method == 'POST': # If the form has been submitted...
        form = UniqueTriggerForm(request.POST)
        if form.is_valid():
            try:
                sched = Schedule.objects.get(pk=schedule_id)
                utrigger = UniqueTrigger.objects.get(schedule=sched)
            except UniqueTrigger.DoesNotExist:
                utrigger = UniqueTrigger()
            utrigger.schedule_id = schedule_id
            utrigger.target_date = form.cleaned_data['target_date']
            utrigger.hour = form.cleaned_data['hour']
            utrigger.level = form.cleaned_data['level']
            utrigger.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s/schedule/%(schedule_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id,'schedule_id':schedule_id})
        else:
            return HttpResponse("Erro de Formulario (Falta customizar mensagem de erro)")
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})
        
        
# FileSets

def create_fileset(request, computer_id=None, procedure_id=None):
    if request.method == 'POST': # If the form has been submitted...
        form = FileSetForm(request.POST)
        if form.is_valid():
            fileset = FileSet()
            fileset.procedure_id = procedure_id
            fileset.path = form.cleaned_data['path']
            fileset.save()
            return HttpResponseRedirect('%(script_name)s/computer/%(computer_id)s/procedure/%(procedure_id)s' % {'script_name':request.META['SCRIPT_NAME'],'computer_id':computer_id,'procedure_id':procedure_id})
        else:
            return HttpResponse("Erro de Formulario (Falta customizar mensagem de erro)")
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    

def delete_fileset(request, computer_id=None, procedure_id=None, fileset_id=None):
    if request.method == 'POST':
        try:
            fset = FileSet.objects.get(pk=fileset_id)
        except FileSet.DoesNotExist:
            return HttpResponse('Erro de URL. FileSet nao existe.')
        fset.delete()
        return HttpResponseRedirect('%(script_name)s/computer/%(comp_id)s/procedure/%(proc_id)s' % {'script_name':request.META['SCRIPT_NAME'],'comp_id':computer_id,'proc_id':procedure_id})
    else:
        return HttpResponse('Erro de Metodo. %(met)s eh inesperado (Falta customizar mensagem de erro)' % {'met':request.method})    
