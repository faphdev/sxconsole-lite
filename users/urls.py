'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^add/$', views.CreateUserView),
    url(r'^(?P<email>[^/]+)/delete/$', views.DeleteUserView),
    url(r'^(?P<email>[^/]+)/send_password_reset/$',
        views.SendPasswordResetView),
]
