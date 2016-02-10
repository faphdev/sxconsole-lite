'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from urllib import urlencode
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from sxclient.exceptions import SXClientException

from sxconsole.api import api
from sxconsole import core
from utils.views import ClusterViewMixin, VolumeViewMixin, ActionView
from utils.clusters import create_volume
from . import forms


class CreateVolumeView(ClusterViewMixin, generic.FormView):
    """Adds a volume to the cluster."""
    form_class = forms.NewVolumeForm
    template_name = 'volumes/add_volume.html'
    url_name = 'add_volume'
    title = _("Adding a new volume")

    def get_form_kwargs(self):
        kwargs = super(CreateVolumeView, self).get_form_kwargs()
        kwargs['cluster'] = self.object
        return kwargs

    def form_valid(self, form):
        try:
            create_volume(**form.cleaned_data)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)
        return redirect(self.object)


class VolumeAclView(VolumeViewMixin, generic.TemplateView):
    template_name = 'volumes/volume_acl.html'
    url_name = 'volume_acl'

    @property
    def title(self):
        return self.volume.name

    def get_context_data(self, **kwargs):
        add_user_url = reverse('add_user')
        add_user_url += '?' + urlencode({'next': self.redirect_to_volume.url})
        perms = self.volume.acl
        users_json = json.dumps({
            'setPermUrl': reverse(
                UpdateVolumeAclView.url_name, args=[self.volume.name]),
            'perms': perms
        })
        return super(VolumeAclView, self) \
            .get_context_data(add_user_url=add_user_url, users_json=users_json,
                              **kwargs)


class UpdateVolumeView(VolumeViewMixin, generic.FormView):
    template_name = 'volumes/edit_volume.html'
    form_class = forms.VolumeForm
    url_name = 'edit_volume'

    @property
    def title(self):
        return _("Updating {}").format(self.volume.name)

    def dispatch(self, *args, **kwargs):
        return super(UpdateVolumeView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateVolumeView, self).get_form_kwargs()
        kwargs['cluster'] = self.object
        kwargs['current_size'] = self.volume.size
        return kwargs

    def get_initial(self):
        return {
            'size': self.volume.size,
            'revisions': self.volume.revisions,
        }

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            self.modify_volume(data)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)
        return redirect(self.object)

    def modify_volume(self, data):
        # Dumb API errors if given value is the same as current value
        kwargs = {}
        size, revisions = data['size'], data['revisions']
        if size != self.volume.size:
            kwargs['size'] = size
        if revisions != self.volume.revisions:
            kwargs['maxRevisions'] = revisions
        if kwargs:
            api.modifyVolume(self.volume.name, **kwargs)


class DeleteVolumeView(VolumeViewMixin, generic.FormView):
    template_name = 'volumes/delete_volume.html'
    form_class = forms.DeleteVolumeForm
    url_name = 'delete_volume'

    @property
    def title(self):
        return _("Deleting {}").format(self.volume.name)

    def get_form_kwargs(self):
        kwargs = super(DeleteVolumeView, self).get_form_kwargs()
        kwargs['name'] = self.volume.name
        kwargs['force'] = not self.volume.empty
        return kwargs

    def form_valid(self, form):
        try:
            api.deleteVolume(self.volume.name, force=form.force)
        except SXClientException as e:
            messages.error(self.request, core.get_exception_msg(e))
        return redirect(self.object)


class UpdateVolumeAclView(VolumeViewMixin, ActionView):
    form_class = forms.UpdateUserAclForm
    url_name = 'volume_update_acl'

    def get_form_kwargs(self):
        kwargs = super(UpdateVolumeAclView, self).get_form_kwargs()
        kwargs.update(cluster=self.object)
        return kwargs

    def perform(self, form):
        data = form.cleaned_data
        try:
            self.set_permissions(data)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)

        return self.volume.get_user_acl(data['email'])

    def set_permissions(self, data):
        email = data['email']
        key = '{action}-{perm}'.format(
            action='grant' if data['value'] else 'revoke',
            perm=data['perm'])

        perms = {key: [email]}
        if key == 'grant-manager':
            perms['grant-read'] = perms['grant-write'] = [email]
        api.updateVolumeACL(self.volume.name, perms)
