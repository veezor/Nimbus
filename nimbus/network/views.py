# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from nimbus.network.models import NetworkInterface
from nimbus.shared.views import edit_singleton_model 

@login_required
def network_conf(request):
    return edit_singleton_model( request, "myform.html", 
                                 "nimbus.network.views.network_conf",
                                 model = NetworkInterface )


def redirect_after_update(request):
    ni = NetworkInterface.objects.all()[0]
    ip_address = ni.address
    return render_to_response('redirect.html', locals())
