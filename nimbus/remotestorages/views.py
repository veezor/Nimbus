

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from nimbus.shared.views import render_to_response
from nimbus.remotestorages import models
from nimbus.procedures.models import Procedure, Profile
from nimbus.storages.models import Storage

@login_required
def render(request):
    storage = models.RemoteStorageConf()
    status = models.RemoteStorageStatus()
    used_space = status.disk_usage
    free_space = 100 - used_space
    storage_info = Storage.objects.get(id=1)
    profiles = Profile.objects.filter(storage=storage)
    extra_content = {
        'num_rows':range(4),
        'storage':storage,
        'title': u"Storages Adicionais",
        'profiles': profiles,
        'storage_info':storage_info,
        'status': status,
        'used_space': used_space,
        'free_space': free_space
    }
    return render_to_response(request, "remotestorages_list.html", extra_content)

@login_required
def do_connect(request):
    pass

@login_required
def warnning_alert(request):

    if request.method == "POST":
        try:
            address = request.META['REMOTE_ADDR']
            storage_status = models.RemoteStorageStatus.objects\
                    .get(storage__address=address)
            storage_status.status = models.WARNNING
            storage_status.save()
            #TODO send email alert
            return HttpResponse(status=200)
        except models.RemoteStorageStatus.DoesNotExist, error:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)




@login_required
def critical_alert(request):

    if request.method == "POST":
        try:
            address = request.META['REMOTE_ADDR']
            storage_status = models.RemoteStorageStatus.objects\
                    .get(storage__address=address)
            storage_status.status = models.CRITICAL
            storage_status.save()
            #TODO send email alert
            return HttpResponse(status=200)
        except models.RemoteStorageStatus.DoesNotExist, error:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)


