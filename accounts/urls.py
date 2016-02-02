'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^login/$', views.LoginView, login=False),
    url(r'^logout/$', views.LogoutView),
    url(r'^profile/$', views.ProfileView),
    url(r'^change_password/$', views.ChangePasswordView),

    url(r'^forgot_password/$', views.ForgotPasswordView, login=False),
    url(r'^password_reset/(?P<token>\w+)/$', views.PasswordResetView,
        login=False),
    url(r'^invitation/(?P<token>\w+)/$', views.InvitationView, login=False),

    url(r'^$', views.AdminListView),
    url(r'^invite/$', views.InviteAdminView),
    url(r'^(?P<pk>\d+)/delete$', views.DeleteAdminView),
]
