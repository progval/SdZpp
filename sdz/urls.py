from django.conf.urls.defaults import *

urlpatterns = patterns('sdz.views',
    (r'^$', 'index'),
    (r'^news/$', 'news_index'),
    (r'^news/news-(?P<news_id>[0-9]+)/$', 'show_news'),
    (r'^news/news-(?P<news_id>[0-9]+)/(?P<page>[0-9]+)/$',
        'show_news_comments'),

    (r'^tutos/$', 'tutos_index'),
    (r'^tutos/list/categories/(?P<id>[0-9]+)/$', 'tutos_list_subcategories'),
    (r'^tutos/list/tutorials/(?P<id>[0-9]+)/$', 'tutos_list_tutorials'),
)
