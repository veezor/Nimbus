# -*- coding: utf-8 -*-
# Create your views here.

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.core import serializers

from nimbus.computers.models import Computer
from nimbus.procedures.models import Procedure
from nimbus.shared.views import render_to_response

from django.http import HttpResponse, HttpResponseRedirect


def view(request, object_id=None):
    if object_id:
        computer = Computer.objects.get(id=object_id)
    else:
        computer = None
    computers = Computer.objects.all()
    extra_content = {
        'computer': computer,
        'computers': computers,
        'title': u"Restauração de arquivos"
    }
    return render_to_response(request, "restore_list.html", extra_content)



def get_procedures(request, object_id=None):
    if not object_id:
        message = {'error': 'Erro ao tentar selecionar o computador.'}
        response = simplejson.dumps(message)
        return HttpResponse(response, mimetype="text/plain")
    
    procedures = Procedure.objects.filter(computer=object_id)
    # computer = Computer.objects.get(id=object_id)
    if not procedures.count():
        message = {'error': 'Erro ao tentar selecionar o computador.'}
        response = simplejson.dumps(message)
        return HttpResponse(response, mimetype="text/plain")
    
    # message = {'error': 'Erro ao tentar selecionar o computador.'}
    # response = simplejson.dumps(computer.procedure_set.all())
    response = serializers.serialize("json", procedures)
    return HttpResponse(response, mimetype="text/plain")
    


def get_tree(request, root=None):
    html = """
<ul class="jqueryFileTree" style="display: none;">
<li class="directory collapsed">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-admin/">wp-admin</a>
</li>
<li class="directory collapsed">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-content/">wp-content</a>
</li>
<li class="directory collapsed">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-includes/">wp-includes</a>
</li>
</ul>"""

    html2 = """
<ul class="jqueryFileTree" style="display: none;">
<li class="file ext_htaccess">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/.htaccess">.htaccess</a>
</li>
<li class="file ext_error_log">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/error_log">error_log</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/index.php">index.php</a>
</li>
<li class="file ext_txt">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/license.txt">license.txt</a>
</li>
<li class="file ext_html">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/readme.html">readme.html</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-app.php">wp-app.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-atom.php">wp-atom.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-blog-header.php">wp-blog-header.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-comments-post.php">wp-comments-post.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-commentsrss2.php">wp-commentsrss2.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-config.php">wp-config.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-cron.php">wp-cron.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-feed.php">wp-feed.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-links-opml.php">wp-links-opml.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-load.php">wp-load.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-login.php">wp-login.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-mail.php">wp-mail.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-pass.php">wp-pass.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-rdf.php">wp-rdf.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-register.php">wp-register.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-rss.php">wp-rss.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-rss2.php">wp-rss2.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-settings.php">wp-settings.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/wp-trackback.php">wp-trackback.php</a>
</li>
<li class="file ext_php">
<a href="#" rel="/Users/jonatas/Desktop/maxima_wp/xmlrpc.php">xmlrpc.php</a>
</li>
</ul>
    """
    # return html
    # response = json.dumps(choices)
    # return render_to_response(request, "json.html", {'json': json})
    response = html
    if root == '1':
        response = html2
    return HttpResponse(response, mimetype="text/plain")

# def view(request, object_id):
#     computers = Computer.objects.get(id=object_id)
#     extra_content = {
#         'computer': computers,
#         'title': u"Visualizar computador"
#     }
#     return render_to_response(request, "computers_view.html", extra_content)
