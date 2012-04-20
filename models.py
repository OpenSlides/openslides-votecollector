#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Models for the VoteCollector Plugin.

    :copyright: 2011 by Oskar Hahn
    :license: GNU GPL, see LICENSE for more details.
"""

from django.db import models

from openslides.utils.translation_ext import ugettext as _
from openslides.participant.models import Profile


class Keypad(models.Model):
    user = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('Participant'),
        help_text=_('Empty for anonymous'),
    )
    keypad_id = models.IntegerField(unique=True, verbose_name=_('Keypad ID'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))

    def __unicode__(self):
        if self.user is not None:
            return _('Keypad from %s') % self.user
        return _('Keypad %d') % self.keypad_id

    @models.permalink
    def get_absolute_url(self, link='edit'):
        if link == 'edit':
            return ('votecollector_keypad_edit', [str(self.id)])
        if link == 'delete':
            return ('votecollector_keypad_delete', [str(self.id)])

    class Meta:
        permissions = (
            ('can_manage_votecollector', _('Can manage VoteCollector', fixstr=True)),
        )



