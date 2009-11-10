#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from environment import ENV as E

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import FileSet, Computer, Procedure
from backup_corporativo.bkp.views import global_vars, authentication_required


### FileSets ###
@authentication_required
def delete_fileset(request, fset_id):
    E.update(request)
    if request.method == 'GET':
        E.fset = get_object_or_404(FileSet, pk=fset_id)
        E.msg = _("Please confirm fileset removal.")
        E.template = 'bkp/fileset/delete_fileset.html'
        return E.render()
    elif request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fileset_id)
        comp_id = fset.procedure.computer.id
        fset.delete()
        E.msg = _("Fileset has been successfully removed.")
        location = reverse("view_computer", args=[comp_id])
        return HttpResponseRedirect(location)