# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.computers.models import Computer
from nimbus.procedures.models import Profile, Procedure
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.backup.forms import StorageForm

from nimbus.shared.enums import days, weekdays, levels, operating_systems

def list(request):
    computers = Computer.objects.all()
    profiles = Profile.objects.all()
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
    
    extra_context = {
        'title': u"Criar Backup",
        'computers': computers,
        'profiles': profiles,
        'storages': storages,
        'days': days,
        'weekdays': weekdays,
        'levels': levels,
        'operating_systems': operating_systems,
        'schedules': schedules,
        'filesets': filesets,
    }
    return create_update.create_object( request, 
                                        form_class = StorageForm,
                                        template_name = "backup_create.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/computers/")


def add(request):
    if request.method == "POST":
        print request.POST
        # import pdb; pdb.set_trace()
        
        ### Campos que serão recebidos nesta função:
        
        # procedure_name - str
        # computer_id - int
        # profile_id - int
        # 
        # profile.storage_id - int
        # profile.schedule_id - int
        # profile.fileset_id - int
        # 
        # schedule.monthly.active - bool
        # schedule.monthly.day - list
        # schedule.monthly.hour - str
        # schedule.monthly.level - int
        # 
        # schedule.weekly.active - bool
        # schedule.weekly.day - list
        # schedule.weekly.hour - str
        # schedule.weekly.level - int
        # 
        # schedule.dayly.active - bool
        # schedule.dayly.day - list
        # schedule.dayly.hour - str
        # schedule.dayly.level - int
        # 
        # schedule.hourly.active - bool
        # schedule.hourly.day - list
        # schedule.hourly.hour - str
        # schedule.hourly.level - int
        

