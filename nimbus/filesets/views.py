# -*- coding: utf-8 -*-

import traceback
import socket
import simplejson

from copy import copy
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import widgets
from django.utils.translation import ugettext as _

from nimbus.filesets.models import FileSet, FilePath, Wildcard
from nimbus.computers.models import Computer, NimbusClientMessageError
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form_mapping, form_from_model
from nimbus.libs.bacula import call_reload_baculadir
from nimbus.libs.db import Session
from nimbus.shared import utils
from nimbus.filesets import forms
# import pdb

@login_required
def add(request, computer_id=None):
    computer = get_object_or_404(Computer, pk=computer_id)
    referer = utils.Referer(request)
    fileset_form = forms.FileSetForm(prefix="fileset")
    hide_name = False
    if referer.local == '/procedures/profile/list/':
        fileset_form.initial = {'is_model': True}
    elif referer.local.startswith('/procedures/'):
        fileset_form.initial = {'name': _('File set of %s') % computer.name}
        hide_name = True
    content = {'title': _(u"Create new file sets"),
               'computer': computer,
               'fileset_form': fileset_form,
               'hide_name': hide_name}
    return render_to_response(request, "add_fileset.html", content)


@login_required
def do_add(request):
    if request.method == 'POST':
        data = request.POST
        fileset_form = forms.FileSetForm(data, prefix="fileset")
        if fileset_form.is_valid():
            new_fileset = fileset_form.save()
            filepaths_form = forms.FilesFormSet(data, instance=new_fileset)
            if filepaths_form.is_valid():
                filepaths_form.save()
                wildcards_form = forms.WildcardsFormSet(data, instance=new_fileset)
                if wildcards_form.is_valid():
                    wildcards_form.save()
                    return HttpResponse('{"status":true,"fileset_id":"%s","fileset_name":"%s","message":_("File sets \'%s\' was created successfully")}' % (new_fileset.id, new_fileset.name, new_fileset.name))
                else:
                    filepaths_form.delete()
                    new_fileset.delete()
                    return HttpResponse('{"status":false,"fileset_id":"none","message":_("Filter errors"),"error":1}')
            else:
                new_fileset.delete()
                return HttpResponse('{"status":false,"fileset_id":"none","message":_("File errors"),"error":1}')
        else:
            return HttpResponse('{"status":false,"fileset_id":"none","message":_("fileset errors"),"error":0}')


@login_required
def edit(request, fileset_id, computer_id):
    f = FileSet.objects.get(id=fileset_id)
    fileset_form = forms.FileSetForm(prefix="fileset", instance=f)
    deletes_form = forms.FilesToDeleteForm(instance=f)
    computer = get_object_or_404(Computer, pk=computer_id)
    content = {'title': _(u"Edit file sets '%s'") % f.name,
               'computer': computer,
               'fileset_form': fileset_form,
               'deletes_form': deletes_form,
               'fileset': f}
    return render_to_response(request, "edit_fileset.html", content)


@login_required
def do_edit(request, fileset_id):
    f = FileSet.objects.get(id=fileset_id)
    if request.method == 'POST':
        data = request.POST
        fileset_form = forms.FileSetForm(data, prefix="fileset", instance=f)
        if fileset_form.is_valid():
            new_fileset = fileset_form.save()
            filepaths_form = forms.FilesToDeleteForm(data, instance=new_fileset)
            if filepaths_form.is_valid():
                filepaths_form.save()
                wildcards_form = forms.WildcardsFormSet(data, instance=new_fileset)
                if wildcards_form.is_valid():
                    for wildcard in new_fileset.wildcards.all():
                        wildcard.delete()
                    new_fileset.save()
                    wildcards_form.save()
                call_reload_baculadir()
                return HttpResponse('{"status":true,"fileset_id":"%s","fileset_name":"%s","message":_("file sets \'%s\' was update successfully")}' % (new_fileset.id, new_fileset.name, new_fileset.name))
            else:
                new_fileset.delete()
                return HttpResponse('{"status":false,"fileset_id":"none","message":_("File errors"),"error":1}')
        else:
            return HttpResponse('{"status":false,"fileset_id":"none","message":_("Fileset errors"),"error":0}')
    
@login_required
def get_tree(request):
    if request.method == "POST":
        try:
            path = request.POST['path']
            computer_id = request.POST['computer_id']
            try:
                computer = Computer.objects.get(id=computer_id)
                files = computer.get_file_tree(path)
                response = simplejson.dumps(files)
            except socket.error, error:
                response = simplejson.dumps({"type" : "error",
                                             "message" :_("Unable to connect to client")})
            except Computer.DoesNotExist, error:
                response = simplejson.dumps({"type" : "error",
                                             "message" : _("Computer not exists")})
            except NimbusClientMessageError, error:
                response = simplejson.dumps({"type" : "error",
                                             "message" : _("Client Nimbus error")})
            return HttpResponse(response, mimetype="text/plain")
        except Exception:
            traceback.print_exc()

@login_required
def delete(request, fileset_id):
    f = get_object_or_404(FileSet, pk=fileset_id)
    procedures = f.procedures.all()
    content = {'fileset': f,
               'procedures': procedures}
    return render_to_response(request, "remove_fileset.html", content)


@login_required
def do_delete(request, fileset_id):
    f = get_object_or_404(FileSet, pk=fileset_id)
    if f.is_model:
        for procedure in f.procedures.all():
            novo_fileset = FileSet()
            novo_fileset.name = _('File of %s') % procedure.name
            novo_fileset.save()
            for file in f.files.all():
                novo_arquivo = FilePath()
                novo_arquivo.fileset = novo_fileset
                novo_arquivo.path = file.path
                novo_arquivo.save()
            for w in f.wildcards.all():
                novo_wildcard = Wildcard()
                novo_wildcard.expression = w.expression
                novo_wildcard.kind = w.kind
                novo_wildcard.fileset = novo_fileset
                novo_wildcard.save()
            procedure.fileset = novo_fileset
            procedure.save()
    name = f.name
    f.delete()
    call_reload_baculadir()
    messages.success(request, _(u"File sets profile '%s' was removed successfully.") % name)
    return redirect('/procedures/profile/list')


@login_required
def reckless_discard(request):
    if request.method == 'POST':
        fileset_id = request.POST["fileset_id"]
        f = get_object_or_404(FileSet, pk=fileset_id)
        # not so reckless
        if not f.procedures.all():
            f.delete()
        # else:
            # leave it to garbage colletor
    return HttpResponse("")
