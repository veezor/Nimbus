# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.computers.models import Computer




def add(request):
    return create_update.create_object( request, 
                                        model = Computer,
                                        template_name = "genericform.html")



def edit(request, object_id):
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Computer,
                                        template_name = "genericform.html")



def delete(request):
    pass

def list(request):
    pass


