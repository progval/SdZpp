# -*- coding: utf8 -*-

###
# Copyright (c) 2011, Valentin Lorentz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import re
import urllib
import urllib2

from django.http import Http404
from django.http import HttpResponse

from phonyproxy.common.templates import render_template
from sdz.common import *

regexp_big_cat = re.compile('<a href="forum-89-(?P<id>[0-9]+)-[^>]*.html">(?P<name>[^<]+)</a>')
regexp_sub_cat = re.compile('<a href="forum-81-(?P<id>[0-9]+)-[^>]*.html">(?P<name>[^<]+)</a>')
regexp_sub_cat_desc = re.compile('<span class="fontsize_08">(?P<description>[^<]+)</span>')

def index(request):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/forum.html')
    lines = response.read().split('\n')
    stage = 0
    categories = []
    currentCategory = None
    currentSubCategory = None
    for line in lines:
        if stage == 0 and '<table class="liste_cat">' in line:
            stage =1
        elif stage == 1:
            matched = regexp_big_cat.search(line)
            if matched is not None:
                currentCategory = Empty()
                currentCategory.id = matched.group('id')
                currentCategory.name = matched.group('name')
                currentCategory.subCategories = []
                categories.append(currentCategory)
            matched = regexp_sub_cat.search(line)
            if matched is not None:
                currentSubCategory = Empty()
                currentSubCategory.id = matched.group('id')
                currentSubCategory.name = matched.group('name')
                currentSubCategory.description = ''
                currentSubCategory.subCategories = []
                currentCategory.subCategories.append(currentSubCategory)
            matched = regexp_sub_cat_desc.search(line)
            if matched is not None:
                currentSubCategory.description += matched.group('description') + '\n'
    return HttpResponse(render_template('sdz/forums/index.html', request,
                                        {'categories': categories}))
