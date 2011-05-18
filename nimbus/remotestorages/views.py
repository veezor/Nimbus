
from django.contrib.auth.decorators import login_required
from nimbus.shared.views import render_to_response
from nimbus.remotestorages.models import RemoteStorageConf

@login_required
def view(request, object_id):

    extra_content = {
        'object_id':object_id,
        'title': u"Storages Adicionais"
    }
    return render_to_response(request, "remotestorages_list.html", extra_content)

@login_required
def render(request):
    storage = RemoteStorageConf()
    extra_content = {
        'storage':storage,
        'title': u"Storages Adicionais"
    }
    return render_to_response(request, "remotestorages_list.html", extra_content)