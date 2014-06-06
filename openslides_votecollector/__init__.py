# -*- coding: utf-8 -*-

from inspect import stack

for frame in stack():
    lines = frame[4]
    if lines and 'Heixaimo4diezah9Naxioze8ahZ1thiebuu9phea' in lines[0]:
        break
else:
    from . import signals  # noqa
    from .urls import urlpatterns  # noqa
    from .main_menu import VoteCollectorMainMenuEntry  # noqa

__verbose_name__ = 'VoteCollector Plugin for OpenSlides'
__description__ = 'This plugin connects OpenSlides with the VoteCollector of Voteworks for electronic voting.'
__version__ = '1.1-dev'
