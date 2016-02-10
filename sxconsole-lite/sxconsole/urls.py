'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.conf.urls import include

from utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^$', views.SuperAdminHomeView),
    url(r'^stats/$', views.StatsView),
    url(r'^stats/initial/$', views.InitialStatsView),
    url(r'^stats/get/$', views.GetStatsView),

    url(r'^admins/', include('accounts.urls')),
    url(r'^users/', include('users.root_urls')),
    url(r'^clusters/', include('clusters.urls')),

    url(r'^', include('django.conf.urls.i18n')),
]
