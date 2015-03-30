from django.conf.urls.defaults import patterns, include, url
from mysite.views import home, oauth2, weibo_login, posts , users
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^oauth2/',oauth2),
    url(r'^weibo_login/',weibo_login),
    url(r'^posts/([0-9a-z]+)', posts),
    url(r'^users', users)
    # Examples:
    # url(r'^$', 'SOA.views.home', name='home'),
    # url(r'^SOA/', include('SOA.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
