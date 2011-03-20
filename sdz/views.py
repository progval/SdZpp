# -*- coding: utf8 -*-
import re
import urllib
import urllib2
import feedparser

from django.http import Http404
from django.http import HttpResponse

from common.templates import render_template

SPLITTER = '" alt="" />'
regexp_smiley = re.compile(r'<img src="/?Templates/images/smilies/[^"]+" alt="([^"]+)" class="smilies"/>')
regexp_html_tag = re.compile(r'<.*?>')
regexp_id_in_news_link = re.compile(r'http://www.siteduzero.com/news-62-'
                                     '(?P<id>[0-9]+)-.*.html')
regexp_member_link = re.compile(r'<a (class="auteur_tut")? href="membres-294-(?P<id>[0-9]+).html">(<span [^>]+>)?(?P<name>[^<]+)(</span>)?</a>')
regexp_h1 = re.compile(r'<h1>(?P<title>.*)</h1>')
regexp_start_news_comments = re.compile(r'<table class="liste_messages">')
regexp_comments_page_link = re.compile(r'<a href=".*.html#discussion">(?P<id>[0-9]+)</a>')
regexp_comments_current_page_link = re.compile(r'<span class="rouge">[0-9]+</span>')
regexp_start_comment = re.compile(r'.*<div class="message_txt">(?P<message>.*)$')
regexp_tuto_link = re.compile(r'<a href="/tutoriel-3-(?P<id>[0-9]+)-[^>]+.html">(?P<name>[^<]+)</a>')
regexp_tuto_cat_link = re.compile(r'<div class="infobox bouton_tuto">[^<]*<h3>(?P<name>[^<]+)</h3>[^<]*'
                                   '<span class="image_cat">[^<]*'
                                   '<a href="tutoriel-(?P<mode>[12])-(?P<id>[0-9]+)-[^.]+.html"[^t]*'
                                   'title="(?P<description>[^>]+)">')
regexp_tuto_tuto_link = re.compile(r'<a href="tutoriel-3-(?P<id>[0-9]+)-[^.]+.html">(<strong>)?(?P<name>[^<]+)(</strong>)?</a>')
regexp_license = re.compile(r'<img src="Templates/images/licences/[^"]+" alt="[^"]+" title="(?P<name>[^"]+)" /></a>')
regexp_tuto_subpart_link = re.compile(r'<a href="#ss_part_(?P<id>[0-9]+)" >(?P<name>[^<]+)</a>')

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
    return code

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
    context = {}
    return HttpResponse(render_template('sdz/index.html', request, context))

def news_index(request):
    return HttpResponse(render_template('sdz/list_news.html', request,
                                        {'news_list': get_news_list()}))

def show_news(request, news_id):
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

def show_news_comments(request, news_id, page):
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
            elif 'Posté le ' in line:
                currentMessage.posted_on = line[-len('xx/xx/xxxx xx:xx:xx'):]
            elif not hasattr(currentMessage, 'content'):
                matched = regexp_start_comment.search(line)
                if matched is None:
                    continue
                else:
                    currentMessage.content = matched.group('message')
            elif '<div class="signature">' in line:
                currentMessage.content = currentMessage.content[:-len('</div>\n\t\n')]
                currentMessage.content = zcode_parser(currentMessage.content)
                messages.append(currentMessage)
                currentMessage = None
            elif '<tr class="header_message">' in line: # No signature
                currentMessage.content = currentMessage.content[:-len('</div>'
                                                '\n\t\t\t\t </td>\n\t</tr>\n')]
                currentMessage.content = zcode_parser(currentMessage.content)
                messages.append(currentMessage)
                currentMessage = None
            else:
                currentMessage.content += line
    return HttpResponse(render_template('sdz/view_news_comments.html', request,
                                        {'title': title,
                                         'page_id': page,
                                         'page_ids': page_ids,
                                         'comments': messages}))


def tutos_index(request):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/tutoriel-1-3-cours.html')
    lines = response.read().split('\n')
    stage = 0
    interesting_content = ''
    for line in lines:
        if stage == 0 and '<div class="box_menu">' in line:
            stage = 1
        elif stage == 1 and 'Templates/images/die.png' in line:
            break
        else:
            interesting_content += line
    raw_tutos = regexp_tuto_link.findall(interesting_content)
    tutos = []
    for raw_tuto in raw_tutos:
        tuto = Empty()
        tuto.id, tuto.name = raw_tuto
        tuto.name = tuto.name.strip()
        tutos.append(tuto)
    return HttpResponse(render_template('sdz/tutos_index.html', request,
                                        {'tutos': tutos}))

def tutos_list_subcategories(request, id):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/tutoriel-1-%s-cours.html' % id)
    lines = response.read().split('\n')
    stage = 0
    interesting_content = ''
    for line in lines:
        if stage == 0 and 'Les tutoriels préférés des Zéros' in line:
            stage = 1
        elif stage == 1 and '<div id="footer">' in line:
            break
        elif stage == 1:
            interesting_content += line
    raw_categories = regexp_tuto_cat_link.findall(interesting_content)
    categories = []
    for raw_category in raw_categories:
        category = Empty()
        category.name, category.mode, category.id, category.description = raw_category
        categories.append(category)
    return HttpResponse(render_template('sdz/tutos_list_subcategories.html', request,
                                        {'categories': categories}))

def tutos_list_tutorials(request, id):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/tutoriel-2-%s-cours.html' % id)
    lines = response.read().split('\n')
    stage = 0
    interesting_content = ''
    for line in lines:
        if stage == 0 and '<table class="liste_cat" summary="Liste des tutoriels">' in line:
            stage = 1
        elif stage == 1 and '<div id="footer">' in line:
            break
        elif stage == 1:
            interesting_content += line
    raw_tutorials = regexp_tuto_tuto_link.findall(interesting_content)
    tutorials = []
    for raw_tutorial in raw_tutorials:
        tutorial = Empty()
        tutorial.id, foo, tutorial.name, foo = raw_tutorial
        tutorials.append(tutorial)
    return HttpResponse(render_template('sdz/tutos_list_tutorials.html', request,
                                        {'tutorials': tutorials}))

def tuto_view(request, id):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/tutoriel-3-%s-foo.html' % id)
    lines = response.read().split('\n')
    stage = 0
    authors = []
    tuto_type = None
    subparts = []
    content = ''
    for line in lines:
        if stage == 0 and line == '<h1>':
            stage = 1
        elif stage == 1:
            title = line.strip()
            stage = 2
        elif stage == 2 and '<strong>Auteur' in line: # May be "Auteur" or "Auteurs"
            stage = 3
        elif stage == 3:
            matched = regexp_member_link.search(line)
            if '<br />' in line:
                stage = 4
            elif matched is None:
                continue
            else:
                authors.append(Member(matched))
        elif stage == 4 and '<strong>Licence</strong>' in line:
            license = line.split(' : ')[1][0:-len('<br /><br />')]
            matched = regexp_license.search(license)
            if matched is not None:
                license = matched.group('name')
            stage = 5
        elif stage == 5 and '<div id="chap_intro">' in line:
            intro = line[len('<div id="chap_intro">'):]
            tuto_type = 'mini'
            stage = 6
        elif stage == 5 and '<div id="btuto_intro">' in line:
            intro = line[len('<div id="btuto_intro">'):]
            tuto_type = 'big'
            stage = 6
        elif stage >= 6:
            if tuto_type == 'mini':
                if stage == 6 and '<div class="sommaire_chap">' in line:
                    stage = 7
                elif stage == 6:
                    intro += line + '\n'
                elif stage == 7 and '<div class="liens_bas_tuto">' in line:
                    stage = 8
                elif stage == 7:
                    matched = regexp_tuto_subpart_link.search(line)
                    if matched is None:
                        continue
                    else:
                        subpart = Empty()
                        subpart.id = matched.group('id')
                        subpart.name = matched.group('name')
                        subparts.append(subpart)
                elif stage == 8 and '<form ' in line:
                    stage = 9
                elif stage == 8 and '<div class="liens_bas_tuto">' in line:
                    break
                elif stage == 8:
                    content += line + '\n'
                elif stage == 9 and '</form>' in line:
                    stage = 10
                elif stage == 10 and '<div class="liens_bas_tuto">' in line:
                    break
                elif stage == 10:
                    content += line + '\n'
    intro = zcode_parser(intro)
    content = zcode_parser(content)
    assert tuto_type in ('mini', 'big')
    return HttpResponse(render_template('sdz/tutos_view_%s_tuto.html' % tuto_type, request,
                                        {'title': title,
                                         'authors': authors,
                                         'license': license,
                                         'subparts': subparts,
                                         'intro': intro,
                                         'content': content}))


