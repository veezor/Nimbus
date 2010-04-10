from django.template.loader import render_to_string
from codecs import open as file


def render_to_file(filename, template, **kwargs):
    try:
        f = file(filename, "w", encoding="utf-8")
        content = render_to_string(template, kwargs)
        f.write(content) 
    finally:
        f.close()



