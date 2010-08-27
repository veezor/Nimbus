# Create your views here.

from os.path import join
from threading import Thread

from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from nimbus.libs import offsite
from nimbus.offsite.models import UploadRequest, DownloadRequest
from nimbus.shared.views import render_to_response




@login_required
def select_storage(request):
    return render_to_response( request, 
                               "select_storage.html",
                               {"devices" : offsite.list_disk_labels() })





def worker_thread(storage):
    archive_devices = offsite.find_archive_devices()
    for arc_dev in archive_devices:
        dest = join( "/media" , storage )
        manager = offsite.LocalManager(origin=arc_dev, 
                                       destination=dest)
        manager.upload_all_volumes()


@login_required
def copy_files_to_storage(request):

    if request.method == "POST":

        device = request.POST.get("device")

        if not device:
            raise Http404()

        thread = Thread(target=worker_thread, args=(device,))
        thread.start()

        return redirect('nimbus.offsite.views.list_uploadrequest')


@login_required
def list_downloadrequest(request):
    return render_to_response( request, 
                               "list_downloadrequest.html", 
                               {"object_list": 
                                    DownloadRequest.objects.all()})

@login_required
def list_uploadrequest(request):
    return render_to_response( request, 
                              "list_uploadrequest.html", 
                              {"object_list": 
                                    UploadRequest.objects.all()})




