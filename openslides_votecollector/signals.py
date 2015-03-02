# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _, ugettext_lazy

from openslides.config.api import ConfigCollection, ConfigVariable, config
from openslides.config.signals import config_signal
from openslides.core.signals import post_database_setup
from openslides.participant.models import Group
from openslides.projector.api import update_projector
from openslides.projector.projector import Overlay
from openslides.projector.signals import projector_overlays

from .models import Seat
from .seating_plan import setup_default_plan


@receiver(config_signal, dispatch_uid="setup_votecollector_config_page")
def setup_votecollector_config_page(sender, **kwargs):
    """
    Config variables for the votecollector plugin.
    """
    votecollector_method = ConfigVariable(
        name='votecollector_method',
        default_value='both',
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
        # Use CharField instead of URLField to allow domain names
        form_field=forms.CharField(
            label=ugettext_lazy('URL for VoteCollector'),
            help_text=ugettext_lazy('Example: http://localhost:8030')))
    votecollector_vote_started_msg = ConfigVariable(
        name='votecollector_vote_started_msg',
        default_value=_('Please vote now!'),
        form_field=forms.CharField(
            required=False,
            label=ugettext_lazy("Overlay message 'vote started'")))
    votecollector_live_voting = ConfigVariable(
        name='votecollector_live_voting',
        default_value=True,
        form_field=forms.BooleanField(
            label=ugettext_lazy('Use live voting'),
            help_text=ugettext_lazy('Incoming votes will be shown on projector during poll is running.'),
            required=False),
        on_change=update_projector)
    votecollector_seating_plan = ConfigVariable(
        name='votecollector_seating_plan',
        default_value=True,
        form_field=forms.BooleanField(
            label=ugettext_lazy('Show seating plan'),
            help_text=ugettext_lazy('Incoming votes will be shown in seating plan on projector if keypad is seated.'),
            required=False),
        on_change=update_projector)
    votecollector_seats_grey = ConfigVariable(
        name='votecollector_seats_grey',
        default_value=False,
        form_field=forms.BooleanField(
            label=ugettext_lazy('Show grey seats on seating plan'),
            help_text=ugettext_lazy('Incoming votes will be shown in grey on seating plan. You can see only WHICH seat has voted but not HOW.'),
            required=False),
        on_change=update_projector)
    votecollector_in_vote = ConfigVariable(
        name='votecollector_in_vote',
        default_value=0,
        form_field=None)
    votecollector_active_keypads = ConfigVariable(
        name='votecollector_active_keypads',
        default_value=0,
        form_field=None)

    return ConfigCollection(title='VoteCollector',
                            url='votecollector',
                            weight=100,
                            variables=(votecollector_method,
                                       votecollector_uri,
                                       votecollector_vote_started_msg,
                                       votecollector_live_voting,
                                       votecollector_seating_plan,
                                       votecollector_seats_grey,
                                       votecollector_in_vote,
                                       votecollector_active_keypads))


@receiver(post_database_setup, dispatch_uid='openslides_votecollector_add_permissions_to_builtin_groups')
def add_permissions_to_builtin_groups(sender, **kwargs):
    """
    Adds the permissions openslides_votecollector.can_manage_votecollector to the group staff.
    """
    content_type = ContentType.objects.get(app_label='openslides_votecollector', model='keypad')

    try:
        staff = Group.objects.get(pk=4)
    except Group.DoesNotExist:
        pass
    else:
        perm_can_manage = Permission.objects.get(content_type=content_type, codename='can_manage_votecollector')
        staff.permissions.add(perm_can_manage)


@receiver(post_database_setup, dispatch_uid='openslides_votecollector_add_default_seating_plan')
def add_default_seating_plan(sender, **kwargs):
    """
    Adds a default seating plan if there are no seats in the database.
    """
    if Seat.objects.all().exists():
        # Do nothing if there are seats in the database
        return
    setup_default_plan()


@receiver(projector_overlays, dispatch_uid='openslides_votecollector_overlay_message')
def overlay_message(sender, **kwargs):
    """
    Adds an overlay to show the votecollector message in non live voting mode.
    """
    def get_projector_html():
        """
        Returns the html for the votecollector message on the projector.
        """
        if config['votecollector_in_vote']:
            key_yes = "<span class='nobr'><img src='/static/img/button-yes.png'> %s</span>" % _('Yes')
            key_no = "<span class='nobr'><img src='/static/img/button-no.png'> %s</span>" % _('No')
            key_abstention = "<span class='nobr'><img src='/static/img/button-abstention.png'> %s</span>" % _('Abstention')
            message = "%s <br> %s &nbsp; %s &nbsp; %s " % (
                config['votecollector_vote_started_msg'],
                key_yes, key_no, key_abstention)
            value = render_to_string('openslides_votecollector/overlay_votecollector_projector.html', {'message': message})
        else:
            value = None
        return value

    return Overlay(
        name='votecollector_message',
        get_widget_html=None,
        get_projector_html=get_projector_html,
        allways_active=True)
