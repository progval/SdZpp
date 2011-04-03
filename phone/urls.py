from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'phone.common.index'),

    (r'^news/$', 'phone.news.index'),
    (r'^news/news-(?P<news_id>[0-9]+)/$', 'phone.news.show'),
    (r'^news/news-(?P<news_id>[0-9]+)/(?P<page>[0-9]+)/$',
        'phone.news.show_comments'),

    (r'^tutos/$', 'phone.tutos.index'),
    (r'^tutos/list/categories/(?P<id>[0-9]+)/$', 'phone.tutos.list_subcategories'),
    (r'^tutos/list/tutorials/(?P<id>[0-9]+)/$', 'phone.tutos.list_tutorials'),
    (r'^tutos/view/(?P<id>[0-9]+)/$', 'phone.tutos.view'),

    (r'^forums/$', 'phone.forums.index'),
    (r'^forums/categories/(?P<id>[0-9]+)/((?P<page>[0-9]+))?$', 'phone.forums.category'),
    (r'^forums/topics/(?P<id>[0-9]+)/((?P<page>[0-9]+))?$', 'phone.forums.topic'),

    (r'^members/(?P<id>[0-9]+)/$', 'phone.members.profile'),
)
