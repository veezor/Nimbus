

from django.contrib.auth.decorators import login_required
from nimbus.shared.views import render_to_response

@login_required
def view(request, object_id):

    print "view"
    extra_content = {
        'object_id':object_id,
        'title': u"Storages Adicionais"
    }
    return render_to_response(request, "remotestorages_list.html", extra_content)
