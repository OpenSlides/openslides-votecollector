# -*- coding: utf-8 -*-
from . import signals  # noqa


NAME = 'openslides-votecollector'
VERSION = '1.0.4'
DESCRIPTION = 'VoteCollector Plugin for OpenSlides'


def get_name():
    """
    Function for OpenSlides' version page.
    """
    return '%s (%s)' % (DESCRIPTION, NAME)
