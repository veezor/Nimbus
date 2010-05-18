#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyspl import loadconf_from_module, get_product
from pyspl.importlib import get_asset_from_name
from django.conf import settings as djangosettings

class DjangoMiddleware(object):

    def __init__(self):
        self.conf = loadconf_from_module(djangosettings.PYSPL_CONF) 
        self.featuremodel = self.conf['featuremodel']
        self.default_product = get_product(djangosettings.DEFAULT_PRODUCT)

        self.features = {}  # { asset : feature }
        for feature in self.featuremodel.features:
            for asset in feature.assets:
                self.features[asset] = feature


    def process_view(self, request, view, args, kwargs):
        module = get_asset_from_name( view.__module__ )
        feature = self.features.get( module, None)

        if not feature:
            feature = self.features.get( view, None )

        if feature:
            return feature.process_asset( view, *args, **kwargs)
        return None

