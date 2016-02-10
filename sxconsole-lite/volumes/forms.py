'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from django import forms
from django.utils.translation import ugettext_lazy as _

from sizefield.widgets import FileSizeWidget

from sxconsole import core
from sxconsole.api import api
from utils.forms import TwbsForm, FieldOrderMixin
from .validators import validate_volume_size, validate_name


class VolumeForm(TwbsForm, forms.Form):
    size = forms.IntegerField(
        label=_("Size"), widget=FileSizeWidget(),
        validators=[core.size_validator], help_text=_("e.g. 100GB"))
    revisions = forms.IntegerField(
        label=_("Revisions"), required=False,
        validators=[core.revisions_validator], initial=2)

    def __init__(self, *args, **kwargs):
        self.cluster = kwargs.pop('cluster')
        self.current_size = kwargs.pop('current_size', 0)
        super(VolumeForm, self).__init__(*args, **kwargs)

    def clean_size(self):
        size = self.cleaned_data['size']
        valid, msg = validate_volume_size(
            self.cluster, size, self.current_size)
        if valid:
            return size
        else:
            raise forms.ValidationError(msg)


class NewVolumeForm(FieldOrderMixin, VolumeForm):
    name = forms.CharField(label=_("Name"), max_length=50,
                           validators=[core.identifier_validator])
    replicas = forms.IntegerField(label=_("Replicas"), initial=2,
                                  validators=[core.replicas_validator])
    encryption = forms.BooleanField(
        required=False, label=_("Encryption"), help_text=_(
            "Important: only users with Manager permission can initialize "
            "an encrypted volume.\n"
            "The user will be prompted to set a password on first upload."))

    field_order = ('name', 'size', 'revisions', 'replicas', 'encryption')

    def __init__(self, *args, **kwargs):
        super(NewVolumeForm, self).__init__(*args, **kwargs)

        # Disable encryption if it's unavailable
        if not api.has_encryption:
            self.fields.pop('encryption')

    def clean_name(self):
        name = self.cleaned_data['name'].lower()
        valid, msg = validate_name(self.cluster, name)
        if valid:
            return name
        else:
            raise forms.ValidationError(msg)


class DeleteVolumeForm(TwbsForm, forms.Form):
    """Form for deleting a volume."""
    name = forms.CharField(label=_("Name"), max_length=50)

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        self.force = kwargs.pop('force')
        super(DeleteVolumeForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = self.force

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.force and name != self.name:
            raise forms.ValidationError(_("You entered a wrong name!"))


class UpdateUserAclForm(TwbsForm, forms.Form):
    """Toggles a single permission."""
    email = forms.CharField()  # May be a regular username actually
    perm = forms.CharField()
    value = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.cluster = kwargs.pop('cluster')
        super(UpdateUserAclForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """Ensure the user belongs to the cluster."""
        email = self.cleaned_data['email']

        try:
            self.cluster.get_user(email)
            return email
        except ValueError:
            raise forms.ValidationError(_("This user doesn't exist."))

    def clean_perm(self):
        perm = self.cleaned_data['perm'].lower()
        if perm not in ('read', 'write', 'manager'):
            raise forms.ValidationError(_("Invalid permission type"))
        return perm
