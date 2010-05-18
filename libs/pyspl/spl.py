#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import types


from pyspl.importlib import ( split_module_name, 
                              _import, 
                              get_asset_from_name, 
                              get_callback )





class FeatureNotSelected(Exception):
    pass


class ConstrainError(Exception):
    pass




class BaseCache(object):

    def __init__(self, name):
        self.name = name
        self._cache[name] = self


    def __repr__(self):
        return u"%s(%s)" % ( type(self).__name__,
                             self.name )


    @classmethod
    def get_by_name(cls, name):
        return cls._cache[name]





class FeatureModel(BaseCache):
    _cache = {}

    def __init__(self, name, feature_missing_callback=None,
                       check_active_product_callback=None):
        super(FeatureModel, self).__init__(name)
        self.features = set()
        self.feature_missing_callback = feature_missing_callback
        self.check_active_product_callback = check_active_product_callback


    def add_feature(self, feature):
        if isinstance(feature, basestring):
            feature = Feature(feature)
        self.features.add(feature)


    def add_subfeature_to(self, subfeature, feature):
        if isinstance(subfeature, basestring):
            subfeature = Feature(feature)
        feature.add_subfeature(subfeature)


    def create_new_product(self, name, feature_missing_callback=None):
        return Product(name, self, feature_missing_callback)


    def feature_missing(self, asset, feature, context=None):
        if self.feature_missing_callback:
            self.feature_missing_callback(asset, feature, context)
        else:
            raise FeatureNotSelected("This asset '%s' requires %s feature not selected in %s product" %\
                                     (asset.__name__, feature.name, self.name))


    @classmethod
    def from_dict(cls, conf):
        conf = dict(conf) # clone
        name = conf.pop('name')
        feature_callback = get_callback(conf.pop('feature_missing_callback', None))
        product_callback = get_callback(conf.pop('check_active_product_callback', None))

        fm = cls( name, feature_callback, product_callback )
        features = load_features_from_dict( conf['features'] )

        for feature in features:
            fm.add_feature( feature )

        return fm


    @classmethod
    def get_active_product(cls, context=None, name=None):
        if not cls._cache:
            return None

        if not name:
            featuremodel = cls._cache.values()[0]
        else:
            featuremodel = cls.get_by_name(name)

        if featuremodel.check_active_product_callback:
            return featuremodel.check_active_product_callback(context)
        else:
            for product in Product._cache.values():
                if product.active:
                    return product




class Product(BaseCache):

    _cache = {}


    def __init__(self, name, featuremodel, feature_missing_callback=None):
        super(Product, self).__init__(name)
        self.featuremodel = featuremodel
        self.feature_missing_callback = feature_missing_callback
        self.features = set()
        self.active = False
        self._load_mandatory_features()




    def _load_mandatory_features(self):
        stack = list( self.featuremodel.features )

        while stack:
            
            item = stack.pop()

            if isinstance(item, MandatoryFeature):
                self.features.add( item )
                
                mandatories = [ f for f in item.subfeatures \
                                    if isinstance(f, MandatoryFeature) ]
                stack.extend( mandatories )




    def activate(self, context=None):

        active_product = FeatureModel.get_active_product(context)
        if active_product:
            active_product.deactivate()

        self.active = True
        self.check_constrains(context)


    def deactivate(self):
        self.active = False


    def feature_missing(self, asset, feature, context=None):
        if self.feature_missing_callback:
            self.feature_missing_callback(asset, feature, context)
        else:
            self.featuremodel.feature_missing(asset, feature, context)


    def contains_feature(self, feature):
        if feature in self.features:
            return True
        else:
            return False


    def check_constrains(self, context=None):
        for feature in self.features: 
            feature.check_constrains(context)

        for f in self.featuremodel.features: 
            if isinstance(f, AlternativeFeature):
                f.check_constrains( context )


    def add_feature(self, feature):
        self.features.add(feature)


    def add_feature_missing_callback(self, callback):
        self.feature_missing_callback = callback


    def requires(self, feature):
        self.add_feature(feature)


    @classmethod
    def from_dict(cls, conf):
        name = conf['name']
        featuremodel = FeatureModel.get_by_name(conf['featuremodel'])
        features = [ Feature.get_by_name(fname) for fname in conf['features'] ]  
        callback = get_callback(conf.get('feature_missing_callback', None))
        p = cls( name, featuremodel, callback)

        for feature in features:
            p.add_feature( feature )
        return p






class Feature(BaseCache):

    _cache = {}


    def __init__(self, name, parent=None,
                       not_selected_callback=None):
        super(Feature, self).__init__(name)
        self._requires = set()
        self._excludes = set()
        self.subfeatures = set()
        self.parent = parent
        self.assets = set()
        self.not_selected_callback = not_selected_callback


    def get_active(self, context=None):
        product = FeatureModel.get_active_product(context)
        if product.contains_feature(self):
            return True
        else:
            return False


    def check_constrains(self, context=None):
        for feature in self._requires:
            if not feature.get_active(context):
                product =  get_active_product(context)
                raise ConstrainError("Feature %s requires %s but this is not active in product %s" %\
                                     (self.name, feature.name, product.name))
        for feature in self._excludes:
            if feature.get_active(context):
                product =  get_active_product(context)
                raise ConstrainError("Feature %s excludes %s but this is active in product %s" %\
                                     (self.name, feature.name, product.name))

        for f in self.subfeatures: 
            if isinstance(f, AlternativeFeature):
                f.check_constrains( context )
            

    def require(self, feature):
        self._requires.add(feature)

    def requires(self, features):
        self._requires.update(features)

    def exclude(self, feature):
        self._excludes.add(feature)


    def excludes(self, features):
        self._excludes.update(features)

    def add_asset(self, asset):
        self.assets.add(asset)

    def add_subfeature(self, feature):
        feature.parent = self
        self.subfeatures.add(feature)

    def add_subfeatures(self, features):
        for feature in features:
            feature.parent = self
        self.subfeatures.update(features)


    def load_assets_from_dict(self, conf, generate_wrapper=False):
        if not generate_wrapper:
            prefix = conf.get('prefix', '')
            if prefix:
                prefix = prefix + "."
            for asset in conf['assets']:
                self.add_asset( get_asset_from_name( prefix + asset ))
        else:
            for asset in conf['assets']:
                self.make_wrapper_from_name( asset )
            



    def make_wrapper_from_name(self, asset_name):

        asset = get_asset_from_name( asset_name )

        self.assets.add( asset )

        if isinstance(asset, types.ModuleType):
            self.make_module_wrapper( asset )
        else:
            container_name, callable = split_module_name( asset_name )
            container = get_asset_from_name( container_name )
            wrapper = self.make_callable_wrapper( asset )
            setattr( container, callable, wrapper )


    def make_module_wrapper(self,  module):
        sys.modules[module.__name__] = FakeModule( self, module)


    def process_asset(self, asset, *args, **kwargs):
        ctx = { 'args': args, 'kwargs': kwargs}
        if self.get_active(ctx):
            return asset(*args, **kwargs)
        elif self.not_selected_callback:
            return self.not_selected_callback(asset, self, ctx)
                                            
        else:
            product = FeatureModel.get_active_product( ctx )
            return product.feature_missing( asset, self, ctx)




    def make_callable_wrapper(self, asset):

        def wrapper(*args, **kwargs):
            self.process_asset( asset, *args, **kwargs)

        wrapper.__name__ = asset.__name__
        wrapper.__doc__ = asset.__doc__
        wrapper.__dict__ = asset.__dict__
        return wrapper


    def __call__(self, asset): # decorator
        return self.make_callable_wrapper(asset)





class MandatoryFeature(Feature):
    pass

class OptionalFeature(Feature):
    pass


class AlternativeFeatureGroup(BaseCache):
    _cache = {}

    def __init__(self, name):
        super(AlternativeFeatureGroup, self).__init__(name)
        self.group = set()

    def add(self, *args):
        for feature in args:
            self.group.add(feature)
            feature.group = self

    def get_actives(self, context=None):
        return [ feature for feature in self.group if feature.get_active(context)]




class AlternativeFeature(Feature):

    def __init__(self, name):
        super(AlternativeFeature, self).__init__( name )
        self.group = None

    def check_constrains(self, context=None):
        super(AlternativeFeature, self).check_constrains(context)
        active_features = self.group.get_actives(context)
        size = len( active_features )
        if size >= 2:
            feature_names = ",".join([ feature.name for feature in active_features ])
            product = FeatureModel.get_active_product(context)
            raise ConstrainError("Features %s are active in %s product but her are alternatives" %\
                                  (feature_names, product.name ))
        elif size == 0:
            raise ConstrainError("No active features in %s group enable" %\
                                  self.group.name )
        else: # =1
            pass



            
            
class FakeModule(types.ModuleType):

    def __init__(self, feature, asset):
        self.feature = feature
        self.asset = asset
        self.__name__ = asset.__name__
        self.__file__ = asset.__file__
        self.__doc__ = asset.__doc__
        self.__package__ = asset.__package__

    def __getattr__(self, name):

        obj = getattr( self.asset, name )

        if callable(obj):
            return self.feature.make_callable_wrapper( obj )
        else:
            if self.feature.get_active():
                return obj
            else:
                product = FeatureModel.get_active_product()
                product.feature_missing( self.asset, self.feature)



# config

def load_features_from_dict(conf):
    result = []

    for feature_name in conf:

        callback = conf[feature_name].pop('not_selected_callback', None)
        callback = get_callback(callback)

        excludes = conf[feature_name].pop('excludes', [])
        requires = conf[feature_name].pop('requires', [])
        
        type = conf[feature_name].pop('type','mandatory')
        type = type.lower()


        if type == "optional":
            feature = OptionalFeature( feature_name )
        elif type == "alternative":
            groupname = conf[feature_name].pop("group")
            try:
                group = AlternativeFeatureGroup.get_by_name(groupname)
            except KeyError, e:
                group = AlternativeFeatureGroup(groupname)

            feature =  AlternativeFeature( feature_name )
            group.add( feature )

        else:
            feature = MandatoryFeature( feature_name )

        subfeatures = conf[feature_name].get('features', {})
        feature.add_subfeatures( load_features_from_dict(subfeatures ) )
        feature.not_selected_callback = callback
        feature.excludes( excludes )
        feature.requires( requires )
        result.append( feature )


    return result



