# -*- coding: utf-8 -*-

import traceback
import socket
import simplejson
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from nimbus.filesets.models import FileSet, FilePath
from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form_mapping, form_from_model
from nimbus.libs.db import Session
from nimbus.shared import utils
from nimbus.filesets import forms
# import pdb

def name_sugestion(computer_id):
    computer = Computer.objects.get(id=computer_id)
    return "Arquivos de %s" % computer.name

def insert_fileset(POST_data):
    if POST_data.has_key('fileset-name') and (POST_data['fileset-name'] != ''):
        fileset_name = {'fileset-name': POST_data['fileset-name']}
    else:
        fileset_name = {'fileset-name': name_sugestion(POST_data['computer_id'])}
    fileset_form = forms.FileSetForm(fileset_name, prefix="fileset")
    if fileset_form.is_valid():
        new_fileset = fileset_form.save()
        return new_fileset
    else:
        # tratar na interface
        print fileset_form.errors
        return False

def file_list(POST_data):
    files = []
    for key in POST_data:
        if key.startswith("path"):
            files.append(POST_data[key])
    return files

@login_required
def add(request, object_id=None):
    if request.method == "POST":
        files = file_list(request.POST)
        if len(files) > 0:
            new_fileset = insert_fileset(request.POST)
            if new_fileset:
                for path in files:
                    filepath_form = forms.FilePathForm({"fileset": new_fileset.id,"path": path})
                    if filepath_form.is_valid():
                        filepath_form.save()
                    else:
                        # tratar na interface
                        print filepath_form.errors
    lforms = [ forms.FileSetForm(prefix="fileset") ]
    lformsets = [ forms.FilePathForm(prefix="filepath") ]
    formset = forms.FilesFormSet()
    content = {'title':u'Criar Sistema de Arquivos',
               'forms':lforms,
               'formsets':lformsets,
               'computer_id':object_id,
               'formset' : formset}
    return render_to_response(request, "add.html", content)


@login_required
def edit(request, object_id):
    title = u"Editar conjunto de arquivos"
    computers = Computer.objects.filter(active=True,id__gt=1)
    filesets = FileSet.objects.get(id=object_id)
    lforms = [forms.FileSetForm(prefix="fileset")]
    lformsets = [forms.FilePathForm(prefix="filepath")]
    content = {'forms':lforms,
               'formsets':lformsets,
               'title':u"Editar Conjunto de Arquivos",
               'computers':computers,
               'filesets':filesets}
    if request.method == "POST":
        with Session() as session:
            filesetform = form_mapping(FileSet, request.POST, object_id=object_id)
            paths = request.POST.getlist('path')
            if filesetform.is_valid():
                fileset = filesetform.save()
                session.add(fileset)
                paths_to_remove = fileset.files.exclude(path__in=paths)
                for path_to_remove in paths_to_remove:
                    fileset.files.remove(path_to_remove)
                    session.delete(path_to_remove)
                for path in paths:
                    pathmodel, created = FilePath.objects.get_or_create(path=path)
                    pathmodel.filesets.add(fileset)
                    session.add(pathmodel)
                    form = form_from_model(pathmodel)
                    if form.is_valid():
                        pathmodel.save()
            if filesetform.errors:
                session.rollback()
                extra_content = {"title" : title, "errors" : filesetform.errors}
                extra_content.update(utils.dict_from_querydict(request.POST,
                                                               lists=("path",))) 
                return render_to_response(request, 'edit_filesets.html', extra_content)
            else:
                messages.success(request, u"Conjunto de arquivos atualizado com sucesso.")
                return redirect('nimbus.filesets.views.edit', object_id)
    return render_to_response(request, 'edit_filesets.html', content)

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
