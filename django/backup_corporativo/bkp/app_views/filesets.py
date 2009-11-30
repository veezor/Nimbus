#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from environment import ENV

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import FileSet, Computer, Procedure
from backup_corporativo.bkp.views import global_vars, authentication_required


### FileSets ###
@authentication_required
def delete_fileset(request, fset_id):
    E = ENV(request)
    if request.method == 'GET':
        E.fset = get_object_or_404(FileSet, pk=fset_id)
        E.proc = E.fset.procedure
        E.template = 'bkp/fileset/delete_fileset.html'
        return E.render()
    elif request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fset_id)
        proc_id = fset.procedure.id
        fset.delete()
        E.msg = u"Local foi removido permanentemente."
        location = reverse("edit_backup", args=[proc_id])
        return HttpResponseRedirect(location)