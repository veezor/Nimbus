#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import FileSet, Computer, Procedure
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


### FileSets ###
@authentication_required
def delete_fileset(request, fset_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['fset'] = get_object_or_404(FileSet, pk=fset_id)
        #vars_dict['proc'] = vars_dict['fset'].procedure
        #vars_dict['comp'] = vars_dict['proc'].computer
        request.user.message_set.create(
            message="Confirme a remoção do diretório.")
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/fileset/delete_fileset.html',
            return_dict,
            context_instance=RequestContext(request))
    #TODO: separar em dois objetos de view.
    elif request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fileset_id)
        fset.delete()
        request.user.message_set.create(
            message="Diretório foi removido permanentemente.")
        return redirect_back_or_default(
            request,
            default=computer_path(request, computer_id))

