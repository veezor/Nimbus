#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyspl.spl import ( FeatureModel,
                        Product,
                        Feature,
                        OptionalFeature,
                        MandatoryFeature,
                        AlternativeFeature,
                        AlternativeFeatureGroup,
                        ConstrainError,
                        FeatureNotSelected )


from pyspl.importlib import _import


def require_feature(name):
    return Feature.get_by_name(name)

def get_product(name):
    return Product.get_by_name(name)

def get_active_product(ctx):
    return FeatureModel.get_active_product(context=ctx)




def loadconf_from_module( module, generate_wrapper=False ):
    result = {}
    moduleobj = _import( module )
    result["featuremodel"] = FeatureModel.from_dict( moduleobj.featuremodel )

    for attr in dir(moduleobj):
        if attr.endswith("_product"):
            product_conf = getattr(moduleobj,  attr )
            result[attr] = Product.from_dict( product_conf )
        elif attr.endswith("_feature"):
            feature_conf = getattr(moduleobj,  attr )
            feature_name = attr.split("_")[0]
            feature = Feature.get_by_name( feature_name )
            result[attr] = feature.load_assets_from_dict( feature_conf, 
                                                          generate_wrapper )
        else:
            pass

    return result



