# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from nimbus.network.models import NetworkInterface
from nimbus.shared.views import edit_singleton_model 



@login_required
def network_conf(request):
    return edit_singleton_model( request, "myform.html", 
                                 "nimbus.network.views.redirect_after_update",
                                 model = NetworkInterface )


@login_required
def redirect_after_update(request):
    ni = NetworkInterface.objects.all()[0]
    port = (':%s' % request.META['SERVER_PORT']) if request.META['SERVER_PORT'] else ''
    ip_address = ni.address + port
    return render_to_response('redirect.html', locals())
