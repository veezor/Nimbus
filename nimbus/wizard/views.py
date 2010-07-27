# Create your views here.

from functools import wraps

from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import Http404


from nimbus.config.forms import ConfigForm
from nimbus.network.forms import NetworkForm
from nimbus.timezone.forms import TimezoneForm
from nimbus.offsite.forms import OffsiteForm
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.wizard import models


def only_wizard(view):

    @wraps(view)
    def wrapper(request):
        wizard = models.Wizard.get_instance()
        if wizard.has_completed():
            raise Http404()
        else:
            return view(request)
    
    return wrapper


@only_wizard
def start(request):
    return edit_singleton_model( request, "genericform.html", 
                                 "nimbus.wizard.views.timezone",
                                 formclass = ConfigForm )

@only_wizard
def timezone(request):
    return edit_singleton_model( request, "timezoneconf.html", 
                                 "nimbus.wizard.views.offsite",
                                 formclass = TimezoneForm )

@only_wizard
def offsite(request):
    return edit_singleton_model( request, "genericform.html", 
                                 "nimbus.wizard.views.network",
                                 formclass = OffsiteForm )

@only_wizard
def network(request):
    return edit_singleton_model( request, "genericform.html", 
                                 "nimbus.wizard.views.password",
                                 formclass = NetworkForm )

@only_wizard
def password(request):
    user = User.objects.get(id=1)
    if request.method == "GET":
        return render_to_response( request, "genericform.html", 
                                   { "form" : SetPasswordForm(user) })
    elif request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('nimbus.wizard.views.finish')
        else:
            return render_to_response( request, "genericform.html", 
                                      { "form" : SetPasswordForm(user) })
    else:
        raise Http404()

@only_wizard
def finish(request):

    if request.method == "GET":
        wizard = models.Wizard.get_instance()
        wizard.finish()
        return redirect( "nimbus.base.views.home" )

