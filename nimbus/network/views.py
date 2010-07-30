# Create your views here.

from django.contrib.auth.decorators import login_required


from nimbus.network.models import NetworkInterface
from nimbus.shared.views import edit_singleton_model 

@login_required
def network_conf(request):
    return edit_singleton_model( request, "genericform.html", 
                                 "nimbus.network.views.network_conf",
                                 model = NetworkInterface )

