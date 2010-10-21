# -*- coding: utf-8 -*-


import traceback 
from django.contrib import messages
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect

from nimbus.filesets.models import FileSet, FilePath
from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form_mapping, form_from_model
from nimbus.libs.db import Session






def edit(request, object_id):
    fileset = FileSet.objects.get(id=object_id)
    
    if request.method == "POST":


        with Session() as session:
            filesetform = form_mapping(FileSet, request.POST, object_id=object_id)
            # TODO: Corrigir a indentação, o fileset está sendo criado dentro
            # do path.
            if filesetform.is_valid():
                fileset = filesetform.save()
                session.add(fileset)

            paths = request.POST.getlist('path')

            paths_to_remove = fileset.files.exclude(path__in=paths)

            for path_to_remove in paths_to_remove:
                fileset.files.remove(path_to_remove)

            for path in paths:
                pathmodel, created = FilePath.objects.get_or_create(path=path)
                pathmodel.filesets.add( fileset )
                session.add(pathmodel)
                form = form_from_model( pathmodel )
                if form.is_valid():
                    pathmodel.save()


            if filesetform.errors:
                session.rollback()
                ### TODO: tratar erros
            else:
                messages.success(request, u"Conjunto de arquivos atualizado com sucesso.")
                return redirect('nimbus.filesets.views.edit', object_id)

    title = u"Editar conjunto de arquivos"
    computers = Computer.objects.all()
    
    return render_to_response(request, 'base_filesets.html',
                                        locals())
