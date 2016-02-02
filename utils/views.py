'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from __future__ import absolute_import

from urllib import unquote

from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import NewPasswordForm
from clusters.models import cluster


class SingleObjectMixin(generic.detail.SingleObjectMixin):

    @cached_property
    def object(self):
        return self.get_object()


class NewPasswordBase(SingleObjectMixin, generic.FormView):
    """Base class for obtaining a new password."""
    form_class = NewPasswordForm
    success_url = reverse_lazy('home')
    template_name = 'simple_form.html'
    slug_url_kwarg = slug_field = 'token'
    messages = True

    def dispatch(self, *args, **kwargs):
        try:
            return super(NewPasswordBase, self).dispatch(*args, **kwargs)
        except Http404:
            if self.messages:
                messages.error(self.request, _(
                    "You can't use this link because it expired, "
                    "or has been already used up."))
            return self.token_invalid()

    def token_invalid(self):
        return redirect('home')

    def form_valid(self, form):
        self.consume_token(form)
        self.login_user(form)
        return super(NewPasswordBase, self).form_valid(form)

    def consume_token(self, form):
        token = self.object
        password = form.cleaned_data['password']
        token.consume(password)
        if self.messages:
            messages.success(self.request, _(
                "Your password has been changed successfully."))

    def login_user(self, form):
        pass  # Subclasses don't have to implement it


class ClusterViewMixin(object):
    """Selects only the user's clusters."""

    object = cluster

    def get_context_data(self, **kwargs):
        """Add `current_cluster` for sidebar."""
        return super(ClusterViewMixin, self) \
            .get_context_data(current_cluster=self.object, **kwargs)


class VolumeViewMixin(ClusterViewMixin):

    def dispatch(self, *args, **kwargs):
        """Check if this volume exists, raise 404 on error."""
        if self.volume:
            return super(VolumeViewMixin, self).dispatch(*args, **kwargs)
        raise Http404()

    @cached_property
    def volume(self):
        try:
            name = unquote(self.kwargs['name'])
            return self.object.get_volume(name)
        except ValueError:
            return None

    @property
    def redirect_to_volume(self):
        """Redirect to the volume page."""
        from volumes.views import VolumeAclView
        url = reverse(VolumeAclView.url_name, args=[self.volume.name])
        return redirect(url)

    def get_context_data(self, **kwargs):
        return super(VolumeViewMixin, self).get_context_data(
            volume=self.volume, **kwargs)


class UserViewMixin(ClusterViewMixin):

    def dispatch(self, *args, **kwargs):
        """Check if this user exists, raise 404 on error."""
        if self.user:
            return super(UserViewMixin, self).dispatch(*args, **kwargs)
        raise Http404()

    @cached_property
    def user(self):
        try:
            email = unquote(self.kwargs['email'])
            return self.object.get_user(email)
        except ValueError:
            return None

    def get_context_data(self, **kwargs):
        return super(UserViewMixin, self).get_context_data(
            cluster_user=self.user, **kwargs)


class ActionView(generic.edit.BaseFormView):
    http_method_names = [u'post']

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        """Perform the action and return a JsonResponse."""
        data = self.perform(form)
        if not isinstance(data, JsonResponse):
            data = JsonResponse(data)
        return data


class RedirectMixin(object):
    """Utilizes the optional `next` querystring param on form completion."""

    def form_valid(self, form):
        """Login the user."""
        response = super(RedirectMixin, self).form_valid(form)
        url = self.request.GET.get('next')
        if is_safe_url(url):
            return redirect(url)
        return response
