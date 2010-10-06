# -*- coding: utf-8 -*-

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect

from nimbus.filesets.models import FileSet, FilePath
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form

from django.contrib import messages

def edit(request, object_id):
    if request.method == "POST":
        # fileset_name
        # filepath_name
        print request.POST
        # TODO: Adicionar a validação do formulário.
        messages.success(request, u"Conjunto de arquivos atualizado com sucesso.")

    title = u"Editar conjunto de arquivos"
    fileset = FileSet.objects.get(id=object_id)
    return render_to_response(request, 'base_filesets.html',
        locals())

