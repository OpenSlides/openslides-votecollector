# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy, ugettext_noop

from openslides.config.api import config
from openslides.motion.models import MotionPoll
from openslides.participant.models import User


KEYPAD_MAP = ({
    'Y': (ugettext_noop('Yes'), 'green'),
    'N': (ugettext_noop('No'), 'red'),
    'A': (ugettext_noop('Abstention'), 'yellow')})


class Seat(models.Model):
    """
    Model for all seats. A seat has a number and x-axis and y-axis values in
    the seating plan.

    The seats are ordered according to their order in the database table.
    """
    number = models.CharField(
        max_length=255,
        verbose_name=ugettext_lazy('Seat number'),
        help_text=ugettext_lazy('You can use digits and also letters.'))
    seating_plan_x_axis = models.PositiveIntegerField(
        verbose_name=ugettext_lazy('X-axis position in the seating plan'))
    seating_plan_y_axis = models.PositiveIntegerField(
        verbose_name=ugettext_lazy('Y-axis position in the seating plan'))

    class Meta:
        ordering = ('pk',)
        unique_together = (('seating_plan_x_axis', 'seating_plan_y_axis'),)

    def __unicode__(self):
        return self.number

    def clean(self):
        """
        Ensures that a non empty seat number is unique.

        Attention: This method is not uses by save() or bulk_create().
        """
        if self.number != '':
            queryset = self.objects.filter(number=self.number)
            if self.pk is not None:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Seat number must be unique or an empty string.')


class Keypad(models.Model):
    """
    Model for keypads. Leave user field blank for anonymous keypads.
    """
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        unique=True,
        verbose_name=ugettext_lazy('Participant'),
        help_text=ugettext_lazy('Leave this field blank for anonymous keypad.'),
    )
    keypad_id = models.IntegerField(unique=True, verbose_name=ugettext_lazy('Keypad ID'))
    seat = models.OneToOneField(
        Seat,
        null=True,
        blank=True,
        verbose_name=ugettext_lazy('Seat'))

    def __unicode__(self):
        if self.user is not None:
            return _('Keypad of %s') % self.user
        return _('Keypad %d') % self.keypad_id

    @models.permalink
    def get_absolute_url(self, link='update'):
        if link == 'update' or link == 'edit':
            return ('votecollector_keypad_edit', [str(self.id)])
        if link == 'delete':
            return ('votecollector_keypad_delete', [str(self.id)])

    @property
    def active(self):
        # Attention: Not all the code uses this property to check whether a
        #            keypad is active or not. Change everythin if you make
        #            some changes here.
        if self.user is not None:
            active = self.user.is_active
        else:
            # Anonymous keypads are always active
            active = True
        return active

    class Meta:
        permissions = (
            ('can_manage_votecollector', ugettext_noop('Can manage VoteCollector')),
        )


class MotionPollKeypadConnection(models.Model):
    """
    Model to connect a poll of a motion with a keypad per personal voting.
    """
    poll = models.ForeignKey(MotionPoll, related_name='keypad_data_list')
    keypad = models.ForeignKey(
        Keypad,
        null=True)
    value = models.CharField(max_length=255)
    serial_number = models.CharField(null=True, max_length=255)

    def get_value(self):
        """
        Returns the vote value as human readable string.
        """
        return _(KEYPAD_MAP[self.value][0])

    def get_css_value(self):
        """
        Returns the value for the css class accordning to the value.
        """
        if config['votecollector_seats_grey']:
            return 'grey'
        else:
            return KEYPAD_MAP[self.value][1]
