#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.signals
    ~~~~~~~~~~~~~~~~~~~~~

    Signals for the VoteCollector Plugin.

    :copyright: 2013 by Oskar Hahn, Emanuel Schütze
    :license: GNU GPL, see LICENSE for more details.
"""

from django.dispatch import receiver
from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy, ugettext_noop

from openslides.config.signals import config_signal
from openslides.config.api import ConfigVariable, ConfigPage


@receiver(config_signal, dispatch_uid="setup_votecollector_config_page")
def setup_votecollector_config_page(sender, **kwargs):
    """
    Config variables for the votecollector plugin.
    """
    votecollector_method = ConfigVariable(
        name='votecollector_method',
        default_value=_('both'),
        form_field=forms.ChoiceField(
            widget=forms.Select(),
            required=False,
            label=ugettext_lazy('Distribution method for keypads'),
            choices=[
                ('anonym', ugettext_lazy('Use anonymous keypads only')),
                ('person', ugettext_lazy('Use personalized keypads only')),
                ('both', ugettext_lazy('Use ananymous and personalized keypads'))]))
    votecollector_uri = ConfigVariable(
        name='votecollector_uri',
        default_value=_('http://localhost:8030'),
        form_field=forms.URLField(
            label=ugettext_lazy('URL for VoteCollector'),
            help_text=ugettext_lazy('Example: http://localhost:8030')))
    votecollector_please_vote = ConfigVariable(
        name='votecollector_please_vote',
        default_value=_('Please vote!<br>1: Yes | 2: No | 3: Abstain'),
        form_field=forms.CharField(
            required=False,
            label=ugettext_lazy('Overlay message \'Please vote\'')))
    votecollector_thank_for_vote = ConfigVariable(
        name='votecollector_thank_for_vote',
        default_value=_('Voting finished.<br>Thank you for your vote.'),
        form_field=forms.CharField(
            required=False,
            label=ugettext_lazy('Overlay message \'Thank you for your vote\'')))
    votecollector_in_vote = ConfigVariable(
        name='votecollector_in_vote',
        default_value=0,
        form_field=None)
    votecollector_active_keypads = ConfigVariable(
        name='votecollector_active_keypads',
        default_value=0,
        form_field=None)

    return ConfigPage(title=ugettext_noop('VoteCollector'),
                      url='votecollector',
                      required_permission='config.can_manage',
                      weight=30,
                      variables=(votecollector_method,
                                 votecollector_uri,
                                 votecollector_please_vote,
                                 votecollector_thank_for_vote,
                                 votecollector_in_vote,
                                 votecollector_active_keypads
                                 ))

