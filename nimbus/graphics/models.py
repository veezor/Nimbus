#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import types
from datetime import datetime
import cPickle as pickle

from django.db import models, transaction
from django.conf import settings

from nimbus.base.models import SingletonBaseModel


class BaseGraphicData(models.Model):
    last_update = models.DateTimeField(null=False, default=datetime.now, auto_now=True)


    @classmethod
    def from_resource(cls, resource, timestamp):
        """Receive resource value and timestamp and returns a django model"""
        raise TypeError("must be implemented")

    def to_resource(self):
        """Must be return the data and timestamp"""
        raise TypeError("must be implemented")

    class Meta:
        abstract = True




class Config(SingletonBaseModel):
    max_items = models.IntegerField(null=False)
    last_update = models.DateTimeField(null=False, default=datetime.now, auto_now=True)



class Storage(object):

    def __init__(self, config):
        """Initialize storage"""
        raise TypeError("must be implemented")


    def get(self, name, index=0):
        """returns (value,timestamp) of resource name from index"""
        raise TypeError("must be implemented")

    def add(self, name, value, timestamp):
        """add new measure from resource name with timestamp"""
        raise TypeError("must be implemented")


    def list(self, name):
        """list items from resource name with (value, timestamp)"""
        raise TypeError("must be implemented")

    def save(self):
        """persist storage data"""
        raise TypeError("must be implemented")




class FileStorage(Storage):

    def __init__(self, config):
        self.config = config
        self.filename = settings.NIMBUS_GRAPHDATA_FILENAME
        self.data = self._load_data()


    def _load_data(self):
        try:
            with file(self.filename) as f:
                return pickle.load(f)
        except IOError:
            return {}


    def get(self, name, index=0):
        try:
            return self.data[name][index]
        except (KeyError, IndexError):
            raise ResourceItemNotFound("not found")


    def list(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise ResourceItemNotFound("not found")


    def add(self, name, value, timestamp):
        if not name in self.data:
            self.data[name] = []
        self.data[name].insert(0, (value, timestamp))
        if len(self.data[name]) > self.config.max_items:
            del self.data[name][-1]


    def save(self):
        with file(self.filename, "w") as f:
            pickle.dump(self.data, f)




class DBStorage(Storage):

    def __init__(self, config):
        self.config = config
        self.items = set()
        self.models = {}
        self._load_models()
        self.in_transaction = False



    def _get_model(self, path):
        model_class = path.split('.')[-1]
        model_path = ".".join(path.split('.')[:-1])
        model_module = model_path.split('.')[-1]
        model_module = __import__(model_path, fromlist=[model_module])
        Model = getattr(model_module, model_class)
        return Model


    def _load_models(self):
        for resource, model in settings.NIMBUS_GRAPHICS_DB_STORE_MODELS:
            model_cls = self._get_model(model)
            self.models[resource] = model_cls


    def _get_model_from_resource(self, name):
        return self.models[name]



    def _start_transaction(self):
        transaction.enter_transaction_management(using=None)
        transaction.managed(True, using=None)
        self.in_transaction = True


    def get(self, name, index=0):
        try:
            Model = self.models[name]
            model = Model.objects.order_by('-last_update')[index]
            return model.to_resource()
        except (KeyError, IndexError):
            raise ResourceItemNotFound("not found")


    def add(self, name, value, timestamp):
        try:

            if not self.in_transaction:
                self._start_transaction()

            Model = self.models[name]
            model = Model.from_resource(value, timestamp)
            self.items.add(model)

            if Model.objects.count() > self.config.max_items:
                model = Model.objects.order_by('last_update')[0]
                model.delete()
        except KeyError:
            raise ResourceItemNotFound("not found")



    def list(self, name):
        try:
            Model = self.models[name]
            return [ m.to_resource() for m in Model.objects.order_by('-last_update') ]
        except KeyError:
            raise ResourceItemNotFound("not found")


    def save(self):
        transaction.commit()
        transaction.leave_transaction_management(using=None)
        self.in_transaction = False





def resource(function):

    function.__graphic_resource__ = True
    return function




class ResourceNameError(Exception):
    pass


class ResourceItemNotFound(Exception):
    pass


class GraphicsManager(object):



    def __init__(self):
        self.resources = {}
        self.config = Config.get_instance()
        self._load_resources()
        self.storage = self._get_storage()


    def _get_storage(self):
        storage_name = settings.NIMBUS_GRAPHIC_STORE
        storage_class = storage_name.split('.')[-1]
        storage_path = ".".join(storage_name.split('.')[:-1])
        storage_module = storage_path.split('.')[-1]
        storage_module = __import__(storage_path, fromlist=[storage_module])
        Storage = getattr(storage_module, storage_class)
        return Storage(self.config)


    def _get_app_graphic_module(self, appname):
        app = appname.split('.')[-1]
        module = __import__(appname + ".graphic", fromlist=app)
        return module


    def _get_resources_from_module(self, module):
        items_name = [ i for i in dir(module) if not i.startswith('_') ]
        resources = []

        for item_name in list(items_name):
            item_obj = getattr(module, item_name)
            if isinstance(item_obj, types.FunctionType)\
               and hasattr(item_obj, "__graphic_resource__"):
                resources.append(item_obj)

        return resources


    def _get_resources_from_app(self, app):
        module = self._get_app_graphic_module(app)
        return self._get_resources_from_module(module)


    def _list_apps(self):
        return [ app for app in settings.INSTALLED_APPS if app.startswith('nimbus.') ]


    def _update_resources(self, resources):
        for resource in resources:
            name = resource.__name__
            if not name in self.resources:
                self.resources[name] = resource
            else:
                raise ResourceNameError('resource name duplicated')


    def _load_resources(self):
        apps = self._list_apps()
        for app in apps:
            try:
                resources = self._get_resources_from_app(app)
                self._update_resources(resources)
            except ImportError, e:
                pass


    def list_resources(self):
        return self.resources.keys()


    def list_resource(self, name):
        return self.storage.list(name)


    def collect_data(self):
        for name, resource in self.resources.items():
            try:
                last_value, last_timestamp = self.storage.get(name)
            except ResourceItemNotFound:
                last_value, last_timestamp = None, None
            value = resource(last_value, last_timestamp)
            now = datetime.now()
            self.storage.add(name, value, now)
        self.storage.save()

