'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^add/$', views.CreateVolumeView),
    url(r'^(?P<name>[^/]+)/acl$', views.VolumeAclView),
    url(r'^(?P<name>[^/]+)/acl/update/$', views.UpdateVolumeAclView),
    url(r'^(?P<name>[^/]+)/edit/$', views.UpdateVolumeView),
    url(r'^(?P<name>[^/]+)/delete/$', views.DeleteVolumeView),
]
