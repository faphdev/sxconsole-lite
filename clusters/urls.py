'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.conf.urls import include

from utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [

    url(r'^$', views.DisplayClusterView),

    url(r'^volumes/', include('volumes.urls')),
    url(r'^users/', include('users.urls')),
]
