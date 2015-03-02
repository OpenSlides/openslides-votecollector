# -*- coding: utf-8 -*-

from inspect import stack

for frame in stack():
    lines = frame[4]
    if lines and 'Heixaimo4diezah9Naxioze8ahZ1thiebuu9phea' in lines[0]:
        break
else:
    from . import main_menu, signals, slides  # noqa
    from .urls import urlpatterns  # noqa

__verbose_name__ = 'OpenSlides VoteCollector Plugin'
__description__ = 'This plugin connects OpenSlides with the VoteCollector of Voteworks for electronic voting.'
__version__ = '1.2'
