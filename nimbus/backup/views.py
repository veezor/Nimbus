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


# def list(request):
#     computers = Computer.objects.all()
#     
#     extra_content = {
#         'computers': computers,
#         'title': u"Computadores"
#     }
#     return render_to_response(request, "computers_list.html", extra_content)
