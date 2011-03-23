# -*- coding: utf8 -*-
import re
import urllib

from django.http import HttpResponse

from phonyproxy.common.templates import render_template

regexp_smiley = re.compile(r'<img src="/?Templates/images/smilies/[^"]+" alt="([^"]+)"( class="smilies")?/>')
regexp_member_link = re.compile(r'<a( class="auteur_tut")? href="membres-294-(?P<id>[0-9]+).html">'
                                 '(<span [^>]*>)?(?P<name>[^<]+)(</span>)?</a>')

class Empty:
    """Container, passed to the template."""
    pass

class UrlOpener(urllib.FancyURLopener):
    version = 'PhonyProxy'

class Member:
    def __init__(self, matched):
        self.name = matched.group('name')
        self.id = matched.group('id')

def zcode_parser(code):
    code, foo = regexp_smiley.subn(r'\1', code)
    if code.endswith('<'):
        code = code[0:-1]
    return code

def index(request):
    context = {}
    return HttpResponse(render_template('sdz/index.html', request, context))
