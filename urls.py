#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.urls
    ~~~~~~~~~~~~~~~~~~

    URLs list for the VoteCollector Plugin.

    :copyright: 2012 by Oskar Hahn.
    :license: GNU GPL, see LICENSE for more details.
"""

from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse

from views import (Overview, KeypadCreate, KeypadUpdate, StartVoting, StopVoting,
                   GetVotingResults, GetVotingStatus, GetStatus,
                   KeypadDelete, KeypadActivate, KeypadCreateMulti)

urlpatterns = patterns('',
    url(r'^$',
        Overview.as_view(),
        name="votecollector_overview",
    ),

    url(r'^new/$',
        KeypadCreate.as_view(),
        name="votecollector_keypad_new",
    ),

    url(r'^new/multi/$',
        KeypadCreateMulti.as_view(),
        name="votecollector_keypad_new_multi",
    ),

    url(r'^(?P<pk>\d+)/edit/',
        KeypadUpdate.as_view(),
        name="votecollector_keypad_edit",
    ),

    url(r'^(?P<pk>\d+)/del/',
        KeypadDelete.as_view(),
        name="votecollector_keypad_delete",
    ),

    url(r'^(?P<pk>\d+)/activate/',
        KeypadActivate.as_view(),
        {'activate': True },
        name="votecollector_keypad_activate",
    ),

    url(r'^(?P<pk>\d+)/deactivate/',
        KeypadActivate.as_view(),
        {'activate': False },
        name="votecollector_keypad_deactivate",
    ),


    url(r'^start/(?P<pk>\d+)/$',
        StartVoting.as_view(),
        name="votecollector_voting_start",
    ),

    url(r'^stop/(?P<pk>\d+)/$',
        StopVoting.as_view(),
        name="votecollector_voting_stop",
    ),

    url(r'^status/$',
        GetStatus.as_view(),
        name="votecollector_voting_status",
    ),

    url(r'^status/(?P<pk>\d+)/$',
        GetVotingStatus.as_view(),
        name="votecollector_voting_status",
    ),


    url(r'^results/$',
        GetVotingResults.as_view(),
        name="votecollector_voting_results",
    ),
)
