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
regexp_current_page = re.compile('<span class="rouge">(?P<page>[0-9]+)</span>')
regexp_other_page = re.compile('<a href="forum-8[13]-[0-9]*-p[0-9]*-[^.]*.html">(?P<page>[0-9]+)</a>')
regexp_topic_link = re.compile('<a href="forum-83-(?P<id>[0-9]+)-p1-[^.]*.html" title="[^"]*">(?P<title>[^<]+)</a>(<br /><span class="fontsize_08">(?P<subtitle>[^<]+)</span>)?')
regexp_topic_title = re.compile('<h1 class="titre_forum">(?P<title>.*)</h1>')
regexp_start_message = re.compile(r'.*<div class="boite_message">(?P<message>.*)$')

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

def category(request, id, page=None):
    opener = UrlOpener()
    if page is None:
        response = opener.open('http://www.siteduzero.com/forum-81-%s-foo.html' % id)
    else:
        response = opener.open('http://www.siteduzero.com/forum-81-%s-p%s-foo.html' % (id, page))
    lines = response.read().split('\n')
    stage = 0
    pages = []
    topics = []
    for line in lines:
        if stage == 0 and '<table class="liste_cat">' in line:
            stage = 1
        elif stage == 1:
            matched = regexp_current_page.search(line)
            if matched is not None:
                pages.append(matched.group('page'))
                continue
            matched = regexp_other_page.search(line)
            if matched is not None:
                pages.append(matched.group('page'))
                continue
            if '<a href="#"' in line:
                pages.append('...')
            if '</td>' in line:
                stage = 2
        elif stage == 2:
            matched = regexp_topic_link.search(line)
            if matched is not None:
                topic = Empty()
                topic.id = matched.group('id')
                topic.title = matched.group('title')
                topic.subtitle = ''
                if matched.group('subtitle') is not None:
                    topic.subtitle = matched.group('subtitle')
                topics.append(topic)
            if '</table>' in line:
                break
    return HttpResponse(render_template('sdz/forums/category.html', request,
                                        {'topics': topics,
                                         'page_ids': pages}))

def topic(request, id, page=None):
    opener = UrlOpener()
    if page is None:
        response = opener.open('http://www.siteduzero.com/forum-83-%s-foo.html' % id)
    else:
        response = opener.open('http://www.siteduzero.com/forum-83-%s-p%s-foo.html' % (id, page))
    lines = response.read().split('\n')
    stage = 0
    pages = []
    messages = []
    currentMessage = None
    for line in lines:
        if stage == 0:
            matched = regexp_topic_title.search(line)
            if matched is not None:
                topic_title = matched.group('title')
                stage = 1
        elif stage == 1 and '<table class="liste_messages">' in line:
            stage = 2
        elif stage == 2:
            matched = regexp_current_page.search(line)
            if matched is not None:
                pages.append(matched.group('page'))
                continue
            matched = regexp_other_page.search(line)
            if matched is not None:
                pages.append(matched.group('page'))
                continue
            if '<a href="javascript' in line:
                pages.append('...')
            if '</td>' in line:
                stage = 3
        elif stage == 3:
            if '<div id="footer">' in line:
                break
            if currentMessage is None:
                matched = regexp_member_link.search(line)
                if matched is None:
                    continue
                else:
                    currentMessage = Empty()
                    currentMessage.author = Member(matched)
            elif 'Posté ' in line and not hasattr(currentMessage, 'posted_on'):
                currentMessage.posted_on = line[27:]
            elif not hasattr(currentMessage, 'content'):
                matched = regexp_start_message.search(line)
                if matched is None:
                    continue
                else:
                    currentMessage.content = matched.group('message')
            elif '<div class="signature">' in line:
                currentMessage.content = currentMessage.content[:-len('</div>\n\t\t ')]
                currentMessage.content = zcode_parser(currentMessage.content)
                messages.append(currentMessage)
                currentMessage = None
            elif '<tr class="header_message">' in line: # No signature
                currentMessage.content = currentMessage.content[:-len('</div></div>'
                                                '\n\t\t\t\t</td>\n\t</tr>\n')]
                currentMessage.content = zcode_parser(currentMessage.content)
                messages.append(currentMessage)
                currentMessage = None
            else:
                currentMessage.content += line + '\n'
    return HttpResponse(render_template('sdz/forums/topic.html', request,
                                        {'messages': messages,
                                         'page_ids': pages,
                                         'page_id': page,
                                         'topic_title': topic_title}))
