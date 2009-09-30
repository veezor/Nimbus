
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import NimbusSSL
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

@authentication_required
def view_tools(request):
    vars_dict, forms_dict = global_vars(request)

    if request.method == 'GET':
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/tools/index_tools.html',
            return_dict,
            context_instance=RequestContext(request))

@authentication_required
def tools_ssl(request):
    vars_dict, forms_dict = global_vars(request)
    # TODO: Utilizar NimbusUUID aqui para manter registro das chaves geradas
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        ssl = NimbusSSL.build()
        vars_dict['rsa_key'] = ssl.dump_rsa_key()
        vars_dict['certificate'] = ssl.dump_certificate()
        vars_dict['pem'] = ssl.dump_pem()
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/tools/tools_ssl.html',
            return_dict,
            context_instance=RequestContext(request))
