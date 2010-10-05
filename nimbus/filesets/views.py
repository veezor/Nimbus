# -*- coding: utf-8 -*-

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect

from nimbus.filesets.models import FileSet, FilePath
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form

def edit(request, object_id):
    extra_context = {'title': u"Editar conjunto de arquivos"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = FileSet,
                                        form_class = form(FileSet),
                                        template_name = "base_filesets.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/filesets/")