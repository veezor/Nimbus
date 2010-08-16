# Create your views here.


from django.contrib.auth.decorators import login_required
from nimbus.shared.views import render_to_response

@login_required
def home(request):
    return render_to_response(request, "home.html", {})
