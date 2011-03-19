from django.conf.urls.defaults import *

urlpatterns = patterns('sdz.views',
    (r'^$', 'index'),
    (r'^news/$', 'news_index'),
    (r'^news/news-(?P<news_id>[0-9]+)/$', 'show_news'),
)