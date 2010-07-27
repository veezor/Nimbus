# Create your views here.

from nimbus.shared.views import render_to_response
from nimbus.devices.models import Device

@login_required
def list_storages(request):
    return render_to_response( request, 
                               "list_storages.html", 
                               {"object_list": 
                                   Device.objects.all()})
