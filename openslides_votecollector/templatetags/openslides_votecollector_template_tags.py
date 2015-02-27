# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter
def detail_button(poll):
    """
    Returns True if the poll detail button should be shown.
    """
    return (poll.has_votes() and
            (poll.keypad_data_list.exclude(keypad__user__exact=None).exists() or
            poll.keypad_data_list.exclude(serial_number__exact=None).exists()))


@register.filter
def make_anonymous_button(poll):
    """
    Returns True if the poll make anonymous button should be shown.

    It is assumed that the filter detail_button was checked in the template
    before.
    """
    return poll.keypad_data_list.exclude(keypad__exact=None).exists()
