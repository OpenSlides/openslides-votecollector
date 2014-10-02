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
