#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import FileSet, Computer, Procedure
from backup_corporativo.bkp.views import global_vars, authentication_required


### FileSets ###
@authentication_required
def delete_fileset(request, fset_id):
    E.update(request)
    if request.method == 'GET':
        E.fset = get_object_or_404(FileSet, pk=fset_id)
        E.msg = _("Confirme a remoção do diretório.")
        E.template = 'bkp/fileset/delete_fileset.html'
        return E.render()
    elif request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fileset_id)
        fset.delete()
        E.msg = _("Diretório foi removido permanentemente.")
        location = computer_path(request, computer_id)
        return redirect_back(request, default=location)