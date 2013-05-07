#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector
    ~~~~~~~~~~~~~

    VoteCollector Plugin.

    :copyright: 2012-2013 by Oskar Hahn, Emanuel Schütze
    :license: GNU GPL, see LICENSE for more details.
"""

from django.utils.translation import ugettext as _
from . import signals

NAME = _('VoteCollector')
VERSION = (1, 0, 4, 'alpha', 1)
