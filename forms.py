#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.forms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Forms for the VoteCollector Plugin.

    :copyright: 2011 by Oskar Hahn.
    :license: GNU GPL, see LICENSE for more details.
"""

from django import forms
from django.utils.translation import ugettext as _

from openslides.utils.forms import CssClassMixin

from models import Keypad


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


class ConfigForm(forms.Form, CssClassMixin):
    """
    The Form for the config page.
    """
    STATUS = (
        ('anonym', _('Use anonymous keypads only')),
        ('person', _('Use personalized keypads only')),
        ('both', _('Use ananymous and personalized keypads')),
    )
    method = forms.ChoiceField(choices=STATUS, label=_('Distribution method for keypads'), initial='both')
    uri = forms.URLField(label=_('URL for VoteCollector'), help_text=_('Example: http://localhost:8030'))
    please_vote = forms.CharField(required=False, label=_('Overlay message \'Please vote\''))
    thank_for_vote = forms.CharField(required=False, label=_('Overlay message \'Thank you for your vote\''))
