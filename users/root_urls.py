'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^invitation/(?P<token>\w+)/$', views.InvitationView, login=False),
    url(r'^password_reset/(?P<token>\w+)/$', views.PasswordResetView,
        login=False),

    url(r'^success/$', views.PasswordSetView, login=False),
    url(r'^invalid_token/$', views.InvalidTokenView, login=False),
]
