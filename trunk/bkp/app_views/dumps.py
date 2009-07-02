#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

