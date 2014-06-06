# -*- coding: utf-8 -*-

from openslides.utils.main_menu import MainMenuEntry


class VoteCollectorMainMenuEntry(MainMenuEntry):
    verbose_name = 'VoteCollector'
    default_weight = 130
    pattern_name = 'votecollector_overview'
    icon_css_class = 'icon-votecollector'
    stylesheets = ['css/votecollector.css']
    required_permission = 'openslides_votecollector.can_manage_votecollector'
