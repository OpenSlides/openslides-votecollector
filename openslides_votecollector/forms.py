# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from openslides.utils.forms import CssClassMixin

from .models import Keypad, Seat


class KeypadForm(forms.ModelForm, CssClassMixin):
    """
    The Form to create and alter keypad.
    """
    seat = forms.ModelChoiceField(
        required=False,
        queryset=Seat.objects.exclude(number=''))

    class Meta:
        model = Keypad


class KeypadMultiForm(forms.Form, CssClassMixin):
    """
    Form to create several keypads.
    """
    from_id = forms.IntegerField(min_value=1, label=_('From keypad ID'))
    to_id = forms.IntegerField(label=_('... to keypad ID'))
