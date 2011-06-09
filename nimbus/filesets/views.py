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
    if request.method == 'POST':
        data = request.POST
        print data
        fileset_form = forms.FileSetForm(data, prefix="fileset")
        if fileset_form.is_valid():
            new_fileset = fileset_form.save()
            filepaths_form = forms.FilesFormSet(data, instance=new_fileset)
            if filepaths_form.is_valid():
                filepaths_form.save()
                messages.success(request, "Conjunto de arquivos '%s' criado com sucesso" % new_fileset.name)
            else:
                new_fileset.delete()
                messages.error(request, "O conjunto de arquivos não pode ser criado. Problemas nos arquivos escolhidos")
        else:
            messages.error(request, "O conjunto de arquivos não foi criado. Verifique os erros abaixo.")
    content = {'title': u"Criar conjunto de arquivos",
               'computer': computer,
               'fileset_form': fileset_form}
    return render_to_response(request, "add_fileset.html", content)


@login_required
def edit(request, fileset_id, computer_id):
    fileset = get_object_or_404(FileSet, pk=fileset_id)
    computer = get_object_or_404(Computer, pk=computer_id)
    fileset_form = forms.FileSetForm(instance=fileset, prefix="fileset")
    deletes_form = forms.FilesToDeleteForm(instance=fileset)
    content = {'title': u"Editar Conjunto de Arquivos '%s'" % fileset.name,
               'computer': computer,
               'fileset': fileset,
               'fileset_form': fileset_form,
               'deletes_form': deletes_form}
    if request.method == 'POST':
        data = request.POST
        deletes_form = forms.FilesToDeleteForm(data, instance=fileset)
        print deletes_form.is_valid()
        if deletes_form.is_valid():
            deletes_form.save()
    return render_to_response(request, "edit_fileset.html", content)



# @login_required
# def edit(request, fileset_id, computer_id):
#     title = u"Editar conjunto de arquivos"
#     computers = Computer.objects.filter(active=True,id__gt=1)
#     filesets = FileSet.objects.get(id=fileset_id)
#     lforms = [forms.FileSetForm(prefix="fileset")]
#     lformsets = [forms.FilePathForm(prefix="filepath")]
#     content = {'forms':lforms,
#                'formsets':lformsets,
#                'title':u"Editar Conjunto de Arquivos",
#                'computers':computers,
#                'filesets':filesets}
#     if request.method == "POST":
#         with Session() as session:
#             filesetform = form_mapping(FileSet, request.POST, object_id=object_id)
#             paths = request.POST.getlist('path')
#             if filesetform.is_valid():
#                 fileset = filesetform.save()
#                 session.add(fileset)
#                 paths_to_remove = fileset.files.exclude(path__in=paths)
#                 for path_to_remove in paths_to_remove:
#                     fileset.files.remove(path_to_remove)
#                     session.delete(path_to_remove)
#                 for path in paths:
#                     pathmodel, created = FilePath.objects.get_or_create(path=path)
#                     pathmodel.filesets.add(fileset)
#                     session.add(pathmodel)
#                     form = form_from_model(pathmodel)
#                     if form.is_valid():
#                         pathmodel.save()
#             if filesetform.errors:
#                 session.rollback()
#                 extra_content = {"title" : title, "errors" : filesetform.errors}
#                 extra_content.update(utils.dict_from_querydict(request.POST,
#                                                                lists=("path",))) 
#                 return render_to_response(request, 'edit_filesets.html', extra_content)
#             else:
#                 messages.success(request, u"Conjunto de arquivos atualizado com sucesso.")
#                 return redirect('nimbus.filesets.views.edit', object_id)
#     return render_to_response(request, 'edit_filesets.html', content)

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
