from django.template.loader import render_to_string
from codecs import open as file
import logging


def render_to_file(filename, template, **kwargs):
    try:
        logger = logging.getLogger()
        f = file(filename, "w", encoding="utf-8")
        content = render_to_string(template, kwargs)
        try:
            f.write(content) 
        except Exception, e:
            logger.exception("Erro ao gerar arquivo %s" % filename)
        finally:
            f.close()
    except Exception, e:
        logger.exception("Erro ao abrir arquivo %s" % filename)



