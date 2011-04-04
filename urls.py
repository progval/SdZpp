from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^phonyproxy/', include('phonyproxy.foo.urls')),
    (r'^phone/', include('sdzpp.phone.urls')),
    (r'^$', 'sdzpp.root.views.index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/progval/workspace/sdzpp/static'}),
)
