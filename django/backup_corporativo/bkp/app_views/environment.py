from backup_corporativo.bkp.models import Computer
from django.template import RequestContext
from django.shortcuts import render_to_response

class Environment(object):

    def update(self, request):
        # TODO: existe jeito mais elegante que isso?
        self.__dict__ = {}
        self.request = request
        self.script_name = request.META['SCRIPT_NAME']
        self.current_user = request.user
        self.computers = Computer.objects.all()
        self.context = RequestContext(request)

    def _set_user_msg(self, msg):
        self.current_user.message_set.create(message=msg)

    msg = property(fset=_set_user_msg)


    def vars(self):
        return vars(self)

    def render(self):
        return render_to_response(self.template, vars(self), self.context)

    def _request(self):
        return self.request



ENV = Environment()
