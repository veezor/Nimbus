#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import types
import collections
from datetime import datetime
import cPickle as pickle

from django.db import models, transaction
from django.conf import settings

from nimbus.base.models import SingletonBaseModel


class Graphics(object):
    
    def _list_apps(self):
        return [ app for app in settings.INSTALLED_APPS if app.startswith('nimbus.') ]

    def find_graphs(self):
        graph_objects = []
        apps = self._list_apps()
        for app in apps:
            try:
                graph = __import__("%s.graphic" % app, globals(), locals(), ['Graphics'], -1).Graphics()
                graph_objects.append(graph)
            except ImportError, e:
                pass
        return graph_objects
        
    def update_all(self):
        graphs = self.find_graphs()
        for graph in graphs:
            graph.update_db()
    
    def render_blocks(self):
        blocks = []
        graphs = self.find_graphs()
        for graph in graphs:
            blocks += graph.data_to_template()
        return blocks
        
        
        
        
        
        