# -*- coding: utf8 -*-
import re
import urllib
import urllib2
import feedparser

from django.http import Http404
from django.http import HttpResponse

from phonyproxy.common.templates import render_template
from sdz.common import *

SPLITTER = '" alt="" />'
regexp_html_tag = re.compile(r'<.*?>')
regexp_id_in_news_link = re.compile(r'http://www.siteduzero.com/news-62-(?P<id>[0-9]+)-.*.html')
regexp_h1 = re.compile(r'<h1>(?P<title>.*)</h1>')
regexp_start_news_comments = re.compile(r'<table class="liste_messages">')
regexp_comments_page_link = re.compile(r'<a href=".*.html#discussion">(?P<id>[0-9]+)</a>')
regexp_comments_current_page_link = re.compile(r'<span class="rouge">[0-9]+</span>')
regexp_start_comment = re.compile(r'.*<div class="message_txt">(?P<message>.*)$')

def get_news_list():
    feed = feedparser.parse('http://www.siteduzero.com/Templates/xml/news_fr.xml')
    news_list = []
    for entry in feed['entries']:
        news = Empty()
        content = entry['summary_detail']['value']
        splitted = content.split(SPLITTER)
        news.logo = splitted[0][len('<img src="'):]
        news.content = SPLITTER.join(splitted[1:])
        news.short = regexp_html_tag.sub('', news.content)[0:140]
        news.id = regexp_id_in_news_link.match(entry['id']).group('id')
        news.title = entry['title_detail']['value']
        news_list.append(news)
    return news_list

def index(request):
    return HttpResponse(render_template('sdz/list_news.html', request,
                                        {'news_list': get_news_list()}))

def show(request, news_id):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/news-62-%s-foo.html' % news_id)
    lines = response.read().split('\n')
    contributors = []
    content = ''
    title = None
    stage = 0
    for line in lines:
        if stage == 0:
            matched = regexp_h1.match(line)
            if matched is None:
                continue
            else:
                title = matched.group('title')
                stage = 1
        elif (stage == 1 or stage == 1.5) and '</div>' in line:
            stage += 0.5
        elif stage == 1 or stage == 1.5:
            matched = regexp_member_link.search(line)
            if matched is None:
                continue
            else:
                contributors.append(Member(matched))
        elif stage == 2 and '<div class="contenu_news">' in line:
            stage = 3
        elif stage == 3 and line == '<div class="taille_news" ' \
                                    'style="margin-bottom: 15px;">':
            break
        elif stage == 3:
            content += line + '\n'
    content = zcode_parser(content)
    return HttpResponse(render_template('sdz/view_news.html', request,
                                        {'title': title,
                                         'contributors': contributors,
                                         'content': content}))

def show_comments(request, news_id, page):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/news-62-%s-p%s-foo.html'%
                           (news_id, page))
    lines = response.read().split('\n')
    stage = 0
    title = ''
    page_ids = []
    messages = []
    currentMessage = None
    for line in lines:
        if stage == 0:
            matched = regexp_h1.match(line)
            if matched is None:
                continue
            else:
                title = matched.group('title')
                stage = 1
        if stage == 1:
            matched = regexp_start_news_comments.search(line)
            if matched is not None:
                stage = 2
            else:
                continue
        elif stage == 2:
            matched = regexp_comments_page_link.search(line)
            matched_current = regexp_comments_current_page_link.search(line)
            if matched is not None:
                page_ids.append(matched.group('id'))
            elif matched_current is not None:
                page_ids.append(page)
            elif '<a href="' in line and 'Précedente' not in line \
                    and 'Suivante' not in line:
                page_ids.append('...')
            elif '</td>' in line:
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
                currentMessage.posted_on = line[len('\t\t\t\tPosté '):]
            elif not hasattr(currentMessage, 'content'):
                matched = regexp_start_comment.search(line)
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
                currentMessage.content = currentMessage.content[:-len('</div>'
                                                '\n\t\t\t\t</td>\n\t</tr>\n')]
                currentMessage.content = zcode_parser(currentMessage.content)
                messages.append(currentMessage)
                currentMessage = None
            else:
                currentMessage.content += line + '\n'
    return HttpResponse(render_template('sdz/view_news_comments.html', request,
                                        {'title': title,
                                         'page_id': page,
                                         'page_ids': page_ids,
                                         'comments': messages}))




