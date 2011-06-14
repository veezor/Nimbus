

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from nimbus.shared.views import render_to_response
from nimbus.remotestorages import models
from nimbus.procedures.models import Procedure, Profile
from nimbus.storages.models import Storage
from django.views.generic import create_update
from nimbus.shared.forms import form

@login_required
def render(request):
    storage = Storage.objects.get(id=1)
    profiles = Profile.objects.filter(storage=storage)
    storage_conf = models.RemoteStorageConf()
    storage_status = models.RemoteStorageStatus()
    used_space = int(storage_status.disk_usage)
    free_space = 100 - used_space
    # save the stuff
    if request.method == "POST":
        storage.active = int(request.POST.get("active"))
        storage.save()
    #updated extra content
    extra_content = {
        'profiles': profiles,
        'storage': storage,
        'storage_conf': storage_conf,
        'storage_status': storage_status,
        'title': u"Storages Adicionais",
        'used_space': used_space,
        'free_space': free_space
    }
    return render_to_response(request, "remotestorages_list.html", extra_content)

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


