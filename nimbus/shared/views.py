#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.libs.bacula import call_reload_baculadir
from nimbus.shared import forms

from django.http import Http404
from django.views.generic.create_update import update_object, create_object
from django.shortcuts import render_to_response as _render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext





def edit_singleton_model(request, templatename, redirect_to,
                         formclass = None, model = None, extra_context = None):


    if not '/' in redirect_to:
        redirect_to = reverse(redirect_to)

    if not formclass and model:
        formclass = forms.form(model)
    try:
        r = update_object( request, object_id=1,
                           form_class = formclass,
                           model = model,
                           template_name = templatename,
                           post_save_redirect = redirect_to,
                           extra_context = extra_context )
    except Http404, error:
        r = create_object( request,
                           form_class = formclass,
                           model = model,
                           template_name = templatename,
                           post_save_redirect = redirect_to,
                           extra_context = extra_context )
    call_reload_baculadir()
    return r

def render_to_response(request, template, dictionary):
    return _render_to_response( template, dictionary,
                                context_instance=RequestContext(request))


