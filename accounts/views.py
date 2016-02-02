'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from sxconsole import msgs
from utils.decorators import anonymous_only
from utils.views import NewPasswordBase, RedirectMixin
from . import forms
from .models import Admin, PasswordReset

console_app_name = settings.SKIN['console_app_name']


@anonymous_only
class LoginView(RedirectMixin, generic.FormView):
    form_class = forms.AuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home')
    url_name = 'login'
    title = _("Login")

    def form_valid(self, form):
        """Login the user."""
        login(self.request, form.get_user())
        self.request.session['remember'] = form.cleaned_data.get('remember')
        return super(LoginView, self).form_valid(form)


class LogoutView(generic.View):
    url_name = 'logout'

    def post(self, *args, **kwargs):
        """Logout the user."""
        logout(self.request)
        return redirect('home')


class ProfileView(generic.TemplateView):
    template_name = 'accounts/profile.html'
    url_name = 'profile'
    template = _("Profile")


class ChangePasswordView(generic.FormView):
    form_class = forms.ChangePasswordForm
    template_name = 'simple_form.html'
    url_name = 'change_password'
    title = _("Change password")
    success_url = reverse_lazy(ProfileView.url_name)

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs['check_password'] = self.request.user.check_password
        return kwargs

    def form_valid(self, form):
        if not settings.DEMO:
            password = form.cleaned_data['password']

            # Set the password
            self.request.user.set_password(password)
            self.request.user.save()

            # Login the user
            user = authenticate(username=self.request.user.email,
                                password=password)
            login(self.request, user)
        return super(ChangePasswordView, self).form_valid(form)


@anonymous_only
class NewAdminPasswordBase(NewPasswordBase):
    model = PasswordReset

    def login_user(self, form):
        user = authenticate(username=self.object.admin.email,
                            password=form.cleaned_data['password'])
        login(self.request, user)


class InvitationView(NewAdminPasswordBase):
    url_name = 'invitation'
    title = _("Welcome")

    @property
    def help_text(self):
        return _(
            "Welcome to {app_name}! "
            "First, you have to set a password for your account.").format(
                app_name=console_app_name)


class PasswordResetView(NewAdminPasswordBase):
    url_name = 'password_reset'
    title = _("Password reset")
    help_text = _("Enter a new password.")


@anonymous_only
class ForgotPasswordView(generic.FormView):
    form_class = forms.AdminEmailForm
    success_url = reverse_lazy('home')
    template_name = 'simple_form.html'
    url_name = 'forgot_password'
    title = _("Forgot your password?")
    help_text = _("Enter your e-mail address. "
                  "We'll send you a link to recover your account.")

    def form_valid(self, form):
        admin = form.cleaned_data['admin']
        sent = PasswordReset.objects.create(admin=admin) \
            .send_reset(self.request)
        if sent:
            msg = _("We have sent you an e-mail with instructions "
                    "on resetting your password.")
            messages.success(self.request, msg)
        else:
            messages.error(self.request, msgs.failed_to_send_email)
        return super(ForgotPasswordView, self).form_valid(form)


class AdminViewMixin(object):

    def get_queryset(self):
        """Select user's co-admins."""
        return Admin.objects.all()


class AdminListView(AdminViewMixin, generic.ListView):
    """List admins."""
    template_name = 'accounts/admin_list.html'
    context_object_name = 'admins'
    url_name = 'admin_list'
    title = _("Administrators")


class InviteAdminView(generic.CreateView):
    """Invite a new admin through an e-mail link."""
    form_class = forms.AdminForm
    success_url = reverse_lazy(AdminListView.url_name)
    template_name = 'simple_form.html'
    url_name = 'invite'
    title = _("Invite")

    def form_valid(self, form):
        response = super(InviteAdminView, self).form_valid(form)
        sent = PasswordReset.objects.create(admin=self.object) \
            .send_invitation(self.request)
        if sent:
            msg = _("Invitation has been sent to {}").format(self.object.email)
            messages.success(self.request, msg)
        else:
            messages.error(self.request, msgs.failed_to_send_email)
        return response


class DeleteAdminView(generic.DeleteView):
    """Deletes an admin."""
    success_url = reverse_lazy(AdminListView.url_name)
    template_name = 'delete.html'
    url_name = 'admin_delete'

    @property
    def title(self):
        return _("Deleting {email}").format(email=self.object.email)

    def get_queryset(self):
        if self.request.user.is_root_admin:
            qs = Admin.objects.exclude(level=Admin.LEVELS.ROOT_ADMIN)
        else:
            qs = Admin.objects.filter(level=Admin.LEVELS.ADMIN)
        return qs
