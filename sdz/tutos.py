# -*- coding: utf8 -*-
import re
import urllib
import urllib2
import feedparser

from django.http import Http404
from django.http import HttpResponse

from phonyproxy.common.templates import render_template
from sdz.common import *

regexp_tuto_link = re.compile(r'<a href="/tutoriel-3-(?P<id>[0-9]+)-[^>]+.html">(?P<name>[^<]+)</a>')
regexp_tuto_cat_link = re.compile(r'<div class="infobox bouton_tuto">[^<]*<h3>(?P<name>[^<]+)</h3>[^<]*'
                                   '<span class="image_cat">[^<]*'
                                   '<a href="tutoriel-(?P<mode>[12])-(?P<id>[0-9]+)-[^.]+.html"[^t]*'
                                   'title="(?P<description>[^>]+)">')
regexp_tuto_tuto_link = re.compile(r'<a href="tutoriel-3-(?P<id>[0-9]+)-[^.]+.html">(<strong>)?(?P<name>[^<]+)(</strong>)?</a>')
regexp_license = re.compile(r'<img src="Templates/images/licences/[^"]+" alt="[^"]+" title="(?P<name>[^"]+)" /></a>')
regexp_tuto_subpart_link = re.compile(r'<a href="#ss_part_(?P<id>[0-9]+)" >(?P<name>[^<]+)</a>')
regexp_bigtuto_subpart = re.compile(r'[^P]*Partie (?P<id>[0-9]+) : (?P<name>.+)$')
regexp_bigtuto_minituto_link = re.compile(r'<a href="tutoriel-3-(?P<id>[0-9]+)-[^.]*.html" >')
regexp_bigtuto_minituto_name = re.compile(r'[0-9]+\) (?P<name>.*)$')


def index(request):
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
            interesting_content += line + '\n'
    raw_tutos = regexp_tuto_link.findall(interesting_content)
    tutos = []
    for raw_tuto in raw_tutos:
        tuto = Empty()
        tuto.id, tuto.name = raw_tuto
        tuto.name = tuto.name.strip()
        tutos.append(tuto)
    return HttpResponse(render_template('sdz/tutos/index.html', request,
                                        {'tutos': tutos}))

def list_subcategories(request, id):
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
            interesting_content += line + '\n'
    raw_categories = regexp_tuto_cat_link.findall(interesting_content)
    categories = []
    for raw_category in raw_categories:
        category = Empty()
        category.name, category.mode, category.id, category.description = raw_category
        categories.append(category)
    return HttpResponse(render_template('sdz/tutos/list_subcategories.html', request,
                                        {'categories': categories}))

def list_tutorials(request, id):
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
            interesting_content += line + '\n'
    raw_tutorials = regexp_tuto_tuto_link.findall(interesting_content)
    tutorials = []
    for raw_tutorial in raw_tutorials:
        tutorial = Empty()
        tutorial.id, foo, tutorial.name, foo = raw_tutorial
        tutorials.append(tutorial)
    return HttpResponse(render_template('sdz/tutos/list_tutorials.html', request,
                                        {'tutorials': tutorials}))

def view(request, id):
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
                elif stage == 7 and '<h2>' in line:
                    content += line + '\n'
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
            else: # big tuto
                if stage == 6 and '<div id="pre_liste_parties">' in line:
                    stage = 7
                    currentPart = None
                elif stage == 6:
                    intro += line + '\n'
                elif stage == 7:
                    if currentPart is None:
                        matched = regexp_bigtuto_subpart.match(line)
                        if matched is None:
                            continue
                        else:
                            currentPart = Empty()
                            currentPart.minitutos = []
                            currentPart.id = matched.group('id')
                            currentPart.name = matched.group('name')
                            currentMinituto = None
                    elif '<hr ' in line:
                        subparts.append(currentPart)
                        currentPart = None
                    elif currentMinituto is None:
                        matched = regexp_bigtuto_minituto_link.search(line)
                        if matched is None:
                            continue
                        else:
                            currentMinituto = Empty()
                            currentMinituto.id = matched.group('id')
                            currentMinituto.name = None
                            currentPart.minitutos.append(currentMinituto)
                    elif currentMinituto.name is None:
                        matched = regexp_bigtuto_minituto_name.search(line)
                        if matched is None:
                            continue
                        else:
                            currentMinituto.name = matched.group('name')
                            currentMinituto = None

    intro = zcode_parser(intro)
    content = zcode_parser(content)
    assert tuto_type in ('mini', 'big')
    return HttpResponse(render_template('sdz/tutos/view_%s_tuto.html' % tuto_type, request,
                                        {'title': title,
                                         'authors': authors,
                                         'license': license,
                                         'subparts': subparts,
                                         'intro': intro,
                                         'content': content}))


