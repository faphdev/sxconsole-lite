'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from utils.forms import TwbsForm, EmailField, NewPasswordForm, \
    get_password_field
from .validators import validate_email


def _get_message():
    return forms.CharField(label=_("Message"), required=False,
                           widget=forms.Textarea(attrs={'rows': 5}))


def _get_save():
    return forms.BooleanField(label=_("Save as default message"),
                              required=False)


class _InvitationForm(forms.Form):
    """Sub-form for customizing the user invitation."""
    message = _get_message()
    save = _get_save()

    def clean_message(self):
        msg = self.cleaned_data['message']
        if not re.search(r'{{ *link *}}', msg):
            raise forms.ValidationError(_(
                "Please keep the \"{{link}}\" tag in the message. "
                "This is where the invitation link will be placed."))
        return msg.strip()


class UserForm(TwbsForm, forms.Form):
    email = EmailField(max_length=50)
    option = forms.ChoiceField(
        label='',
        choices=(
            ('invite', _("Send an invitation e-mail")),
            ('set_password', _("Set the user's password"))),
        initial='invite',
        widget=forms.RadioSelect())

    message = _get_message()
    save = _get_save()

    password = get_password_field(label=_("Password"), required=False)
    confirm_password = get_password_field(label=_("Confirm password"),
                                          required=False)

    def clean(self):
        """Validate the sub-form."""
        if self.cleaned_data.get('option') == 'set_password':
            form = NewPasswordForm(data=self.cleaned_data)
        elif self.cleaned_data.get('option') == 'invite':
            form = _InvitationForm(data=self.cleaned_data)
        else:
            return  # invalid option, will be handled on field-level validation
        if not form.is_valid():
            raise forms.ValidationError(form.errors)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        valid, msg = validate_email(email)
        if valid:
            return email
        else:
            raise forms.ValidationError(msg)
