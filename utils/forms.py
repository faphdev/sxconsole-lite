'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

from collections import OrderedDict

from django import forms
from django.utils.translation import ugettext_lazy as _
from sxconsole.core import password_validator


class TwbsForm(object):
    """Mixin for adjusting form inputs to twitter bootstrap."""

    def __init__(self, *args, **kwargs):
        super(TwbsForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.RadioSelect):
                self[name].is_radio = True
            elif isinstance(field.widget, forms.CheckboxInput):
                self[name].is_checkbox = True
            else:
                css_class = field.widget.attrs.get('class', '')
                css_class += ' form-control'
                field.widget.attrs['class'] = css_class.strip()


class EmailField(forms.EmailField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', _("Email"))
        super(EmailField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """Lowercase the value."""
        return super(EmailField, self).clean(value).lower()


def get_password_field(**kwargs):
    return forms.CharField(max_length=100, widget=forms.PasswordInput(),
                           validators=[password_validator], **kwargs)


class NewPasswordForm(TwbsForm, forms.Form):
    """Form for specifying a new password."""
    password = get_password_field(label=_("Password"))
    confirm_password = get_password_field(label=_("Confirm password"))

    def clean(self):
        data = self.cleaned_data
        pw1, pw2 = data.get('password'), data.get('confirm_password')
        if pw1 != pw2:
            # Don't check if passwords weren't given (django will handle that)
            if None not in (pw1, pw2):
                raise forms.ValidationError(
                    {'confirm_password': _("Both passwords must match.")})
        return data


class FieldOrderMixin(object):
    """Backport of Django 1.9's `field_order` feature.

    This is useful when inheritance messes up the order of fields.
    """

    field_order = ()

    def __init__(self, *args, **kwargs):
        super(FieldOrderMixin, self).__init__(*args, **kwargs)
        assert len(self.field_order) == len(self.fields)
        self.fields = OrderedDict((name, self.fields[name])
                                  for name in self.field_order)
