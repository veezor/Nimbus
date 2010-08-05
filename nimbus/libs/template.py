#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.template import loader
from codecs import open as file
import logging


def render_to_file(filename, template, **kwargs):
    try:
        logger = logging.getLogger(__name__)
        f = file(filename, "w", encoding="utf-8")
        content = loader.render_to_string(template, kwargs)
        try:
            f.write(content) 
        except Exception, e:
            logger.exception("Erro ao gerar arquivo %s" % filename)
        finally:
            f.close()
    except Exception, e:
        logger.exception("Erro ao abrir arquivo %s" % filename)




def render_to_string(template, **kwargs):
    return loader.render_to_string(template, kwargs)
