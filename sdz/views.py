import re
import urllib
import urllib2
import feedparser

from django.http import Http404
from django.http import HttpResponse

from common.templates import render_template

SPLITTER = '" alt="" />'
regexp_html_tag = re.compile(r'<.*?>')
regexp_id_in_news_link = re.compile(r'http://www.siteduzero.com/news-62-'
                                     '(?P<id>[0-9]+)-.*.html')
regexp_member_link = re.compile(r'<a href="membres-294-(?P<id>[0-9]+).html">(?P<name>.+)</a>')
#                                 <a href="membres-294-154852.html">syriux</a>
regexp_h1 = re.compile(r'<h1>(?P<title>.*)</h1>')

class News:
    """Container, passed to the template."""
    pass

class UrlOpener(urllib.FancyURLopener):
    version = 'PhonyProxy'

class Member:
    def __init__(self, matched):
        self.name = matched.group('name')
        self.id = matched.group('id')

def get_news_list():
    feed = feedparser.parse('http://www.siteduzero.com/Templates/xml/news_fr.xml')
    news_list = []
    for entry in feed['entries']:
        news = News()
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
    return HttpResponse(render_template('sdz/view_news.html', request,
                                        {'title': title,
                                         'contributors': contributors,
                                         'content': content}))


