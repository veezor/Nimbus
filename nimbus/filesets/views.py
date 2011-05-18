# -*- coding: utf-8 -*-

import traceback 
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
import pdb


@login_required
def add(request, object_id=None):
    # just for test, must be removed in production mode
    print "####################################################################"
    if request.method == "POST":
        for i in request.POST:
            print i, request.POST[i]
        print "\n\n"
    if request.method == "GET":
        for i in request.GET:
            print i, request.GET[i]
        print "\n\n"
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
