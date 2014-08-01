from django.conf.urls import patterns, include, url

from django.contrib import admin
from Web_Flash_Driver.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web_u.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^main_old/$', main_old),
    url(r'^(\S+)/$', download),
    url(r'^$', main),
)
