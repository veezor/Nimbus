#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import types
import collections
from datetime import datetime
import cPickle as pickle

from django.db import models, transaction
from django.conf import settings

from nimbus.base.models import SingletonBaseModel


Data = collections.namedtuple('Data', 'value timestamp')


class DataList(list):

    @property
    def values(self):
        return [ data.value for data in self ]

    @property
    def timestamps(self):
        return [ data.timestamp for data in self ]



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

    def size(self, name):
        """size from resource list data"""
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


    def get(self, name, index=-1):
        try:
            return self.list(name)[index]
        except (KeyError, IndexError):
            raise ResourceItemNotFound("not found")


    def list(self, name):
        try:
            return DataList( Data(*d) for d in self.data[name] )
        except KeyError:
            raise ResourceItemNotFound("not found")


    def size(self, name):
        return len(self.list(name))


    def add(self, name, value, timestamp):
        if not name in self.data:
            self.data[name] = []
        self.data[name].append(value, timestamp)
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


    def get(self, name, index=-1):
        try:
            return self.list(name)[index]
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
            models = Model.objects.order_by('last_update')
            return DataList( Data(*m.to_resource()) for m in models )
        except KeyError:
            raise ResourceItemNotFound("not found")


    def save(self):
        transaction.commit()
        transaction.leave_transaction_management(using=None)
        self.in_transaction = False


    def size(self, name):
        return len(self.list(name))



def resource(function):

    function.__graphic_resource__ = True
    return function


def filter_value(function):

    function.__graphic_filter__ = True
    function.__graphic_filter_value__ = True
    return function


def filter(function):

    function.__graphic_filter__ = True
    return function



class PipeLine(object):

    def __init__(self):
        self.filters = {}
        self.filter_values = {}


    def get_filter_values(self):
        return self.filter_values.keys()


    def get_filters(self):
        return self.filter.keys()


    def add(self, filter):
        if hasattr(filter, "__graphic_filter_value__"):
            self.add_filter_value(filter)
        elif hasattr(filter, "__graphic_filter__"):
            self.add_filter(filter)
        else:
            raise TypeError("Invalid Filter")


    def add_filter(self, filter):
        self.filters[filter.__name__] = filter

    def add_filter_value(self, filter):
        self.filter_values[filter.__name__] = filter

    def apply_filter_value(self, resource_name, value):

        for filter in self.filter_values.values():
            value = filter(resource_name, value)

        return value


    def apply_filter(self, resource_name, alist):

        for filter in self.filters.values():
            alist = DataList(filter(resource_name, alist))

        return alist


    def apply(self, resource_name, alist):
        values = DataList( self.apply_filter_value(resource_name, v) for v in alist )
        return self.apply_filter(resource_name, values)



class ResourceNameError(Exception):
    pass


class ResourceItemNotFound(Exception):
    pass


class GraphicsManager(object):



    def __init__(self):
        self.resources = {}
        self.config = Config.get_instance()
        self._load_resources()
        self.pipeline = PipeLine()
        self._load_filters()
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


    def _get_filters_from_module(self, module):
        items_name = [ i for i in dir(module) if not i.startswith('_') ]
        filters = []

        for item_name in list(items_name):
            item_obj = getattr(module, item_name)
            if isinstance(item_obj, types.FunctionType)\
               and hasattr(item_obj, "__graphic_filter__"):
                filters.append(item_obj)

        return filters



    def _get_resources_from_app(self, app):
        module = self._get_app_graphic_module(app)
        return self._get_resources_from_module(module)


    def _get_filters_from_app(self, app):
        module = self._get_app_graphic_module(app)
        return self._get_filters_from_module(module)




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


    def _load_filters(self):
        apps = self._list_apps()
        for app in apps:
            try:
                filters = self._get_filters_from_app(app)
                for filter in filters:
                    self.pipeline.add(filter)
            except ImportError, e:
                pass




    def get_max_items_resources(self):
        return self.config.max_items


    def get_last_collect_time(self):
        return self.config.last_update


    def export_data_to_dict(self):
        data = {}
        for resource_name in self.resources:
            resource = self.resources[resource_name]
            data[resource_name] = {}
            data[resource_name]["doc"] = resource.__doc__
            data[resource_name]["data"] = self.list_resource(resource_name)

        return data

    def list_resources(self):
        return self.resources.keys()


    def list_resource(self, name):
        return self.pipeline.apply(name, self.storage.list(name))

    def get_last_value(self, name):
        return self.pipeline.apply_filter_value(name, self.storage.get(name))


    def collect_data(self, interactive=False):
        for name, resource in self.resources.items():
            value = resource(self, interactive)
            now = datetime.now()
            self.storage.add(name, value, now)
        self.config.save() # update last_update field from config
        self.storage.save()

