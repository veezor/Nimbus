# Create your views here.

from nimbus.shared.views import render_to_response


def home(request):
    return render_to_response(request, "base.html", {})
