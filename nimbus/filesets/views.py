# -*- coding: utf-8 -*-

import traceback
import socket
import simplejson
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from nimbus.filesets.models import FileSet, FilePath
from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form_mapping, form_from_model
from nimbus.libs.db import Session
from nimbus.shared import utils
from nimbus.filesets import forms
# import pdb

@login_required
def add(request, computer_id=None):
    fileset_form = forms.FileSetForm(prefix="fileset")
    computer = get_object_or_404(Computer, pk=computer_id)
    content = {'title': u"Criar conjunto de arquivos",
               'computer': computer,
               'fileset_form': fileset_form}
    return render_to_response(request, "add_fileset.html", content)


@login_required
def do_add(request):
    if request.method == 'POST':
        data = request.POST
        print data
        fileset_form = forms.FileSetForm(data, prefix="fileset")
        if fileset_form.is_valid():
            new_fileset = fileset_form.save()
            filepaths_form = forms.FilesFormSet(data, instance=new_fileset)
            if filepaths_form.is_valid():
                filepaths_form.save()
                return HttpResponse('{"status":true,"fileset_id":"%s","fileset_name":"%s","message":"Conjunto de arquivos \'%s\' foi criado com sucesso"}' % (new_fileset.id, new_fileset.name, new_fileset.name))
            else:
                new_fileset.delete()
                return HttpResponse('{"status":false,"fileset_id":"none","message":"Erro nos arquivos","error":1}')
        else:
            return HttpResponse('{"status":false,"fileset_id":"none","message":"Erro nos fileset","error":0}')


@login_required
def edit(request, fileset_id, computer_id):
    f = FileSet.objects.get(id=fileset_id)
    fileset_form = forms.FileSetForm(prefix="fileset", instance=f)
    deletes_form = forms.FilesToDeleteForm(instance=f)
    computer = get_object_or_404(Computer, pk=computer_id)
    content = {'title': u"Editar Conjunto de Arquivos '%s'" % f.name,
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
        print data
        fileset_form = forms.FileSetForm(data, prefix="fileset", instance=f)
        if fileset_form.is_valid():
            new_fileset = fileset_form.save()
            filepaths_form = forms.FilesToDeleteForm(data, instance=new_fileset)
            if filepaths_form.is_valid():
                filepaths_form.save()
                return HttpResponse('{"status":true,"fileset_id":"%s","fileset_name":"%s","message":"Conjunto de arquivos \'%s\' foi criado com sucesso"}' % (new_fileset.id, new_fileset.name, new_fileset.name))
            else:
                new_fileset.delete()
                return HttpResponse('{"status":false,"fileset_id":"none","message":"Erro nos arquivos","error":1}')
        else:
            return HttpResponse('{"status":false,"fileset_id":"none","message":"Erro nos fileset","error":0}')



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
                                             "message" : "Impossível conectar ao cliente"})
            except Computer.DoesNotExist, error:
                response = simplejson.dumps({"type" : "error",
                                             "message" : "Computador não existe"})
            return HttpResponse(response, mimetype="text/plain")
        except Exception:
            traceback.print_exc()
