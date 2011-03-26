from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'sdz.common.index'),

    (r'^news/$', 'sdz.news.index'),
    (r'^news/news-(?P<news_id>[0-9]+)/$', 'sdz.news.show'),
    (r'^news/news-(?P<news_id>[0-9]+)/(?P<page>[0-9]+)/$',
        'sdz.news.show_comments'),

    (r'^tutos/$', 'sdz.tutos.index'),
    (r'^tutos/list/categories/(?P<id>[0-9]+)/$', 'sdz.tutos.list_subcategories'),
    (r'^tutos/list/tutorials/(?P<id>[0-9]+)/$', 'sdz.tutos.list_tutorials'),
    (r'^tutos/view/(?P<id>[0-9]+)/$', 'sdz.tutos.view'),

    (r'^forums/$', 'sdz.forums.index'),
    (r'^forums/categories/(?P<id>[0-9]+)/((?P<page>[0-9]+))?$', 'sdz.forums.category'),
    (r'^forums/topics/(?P<id>[0-9]+)/((?P<page>[0-9]+))?$', 'sdz.forums.topic'),
)
