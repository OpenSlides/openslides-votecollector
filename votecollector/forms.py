#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.forms
    ~~~~~~~~~~~~~~~~~~~

    Forms for the VoteCollector Plugin.

    :copyright: 2012 by Oskar Hahn.
    :license: GNU GPL, see LICENSE for more details.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from openslides.utils.forms import CssClassMixin

from votecollector.models import Keypad


class KeypadForm(forms.ModelForm, CssClassMixin):
    """
    The Form to create and alter keypad.
    """
    class Meta:
        model = Keypad


class KeypadMultiForm(forms.Form, CssClassMixin):
    """
    Form to create several keypads.
    """
    from_id = forms.IntegerField(min_value=1, label=_('From keypad ID'))
    to_id = forms.IntegerField(label=_('... to keypad ID'))
    active = forms.BooleanField(initial=True, required=False, label=_('Active'))
