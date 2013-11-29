# -*- coding: utf-8 -*-

from django import forms
from django.dispatch import receiver
from django.utils.translation import ugettext as _, ugettext_lazy

from openslides.config.api import ConfigPage, ConfigVariable
from openslides.config.signals import config_signal


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
        default_value='http://localhost:8030',
        form_field=forms.URLField(
            label=ugettext_lazy('URL for VoteCollector'),
            help_text='%s: http://localhost:8030' % ugettext_lazy('Example')))
    votecollector_vote_started_msg = ConfigVariable(
        name='votecollector_vote_started_msg',
        default_value=_('Please vote!<br>1: Yes | 2: No | 3: Abstain'),
        form_field=forms.CharField(
            required=False,
            label=ugettext_lazy("Overlay message 'vote started'")))
    votecollector_vote_closed_msg = ConfigVariable(
        name='votecollector_vote_closed_msg',
        default_value=_('Vote is closed.'),
        form_field=forms.CharField(
            required=False,
            label=ugettext_lazy("Overlay message 'vote closed'")))
    votecollector_in_vote = ConfigVariable(
        name='votecollector_in_vote',
        default_value=0,
        form_field=None)
    votecollector_active_keypads = ConfigVariable(
        name='votecollector_active_keypads',
        default_value=0,
        form_field=None)

    return ConfigPage(title='VoteCollector',
                      url='votecollector',
                      required_permission='config.can_manage',
                      weight=100,
                      variables=(votecollector_method,
                                 votecollector_uri,
                                 votecollector_vote_started_msg,
                                 votecollector_vote_closed_msg,
                                 votecollector_in_vote,
                                 votecollector_active_keypads))
