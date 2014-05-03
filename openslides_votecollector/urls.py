# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import (Overview, KeypadCreate, KeypadUpdate, StatusView,
                    StartVoting, StopVoting, GetVotingResults, GetVotingStatus,
                    GetStatus, KeypadDelete, KeypadSetStatusView, KeypadCreateMulti)

urlpatterns = patterns(
    '',
    url(r'^votecollector/$',
        Overview.as_view(),
        name="votecollector_overview"),

    url(r'^votecollector/new/$',
        KeypadCreate.as_view(),
        name="votecollector_keypad_new"),

    url(r'^votecollector/new/multi/$',
        KeypadCreateMulti.as_view(),
        name="votecollector_keypad_new_multi"),

    url(r'^votecollector/(?P<pk>\d+)/edit/',
        KeypadUpdate.as_view(),
        name="votecollector_keypad_edit"),

    url(r'^votecollector/(?P<pk>\d+)/del/',
        KeypadDelete.as_view(),
        name="votecollector_keypad_delete"),

    url(r'^votecollector/(?P<pk>\d+)/toggle/$',
        KeypadSetStatusView.as_view(),
        {'action': 'toggle'},
        name='votecollector_keypad_status_toggle'),

    url(r'^votecollector/(?P<pk>\d+)/activate/',
        KeypadSetStatusView.as_view(),
        {'action': 'activate'},
        name="votecollector_keypad_activate"),

    url(r'^votecollector/(?P<pk>\d+)/deactivate/',
        KeypadSetStatusView.as_view(),
        {'action': 'deactivate'},
        name="votecollector_keypad_deactivate"),

    url(r'^votecollector/status/$',
        StatusView.as_view(),
        name="votecollector_status"),

    url(r'^votecollector/start/(?P<pk>\d+)/$',
        StartVoting.as_view(),
        name="votecollector_voting_start"),

    url(r'^votecollector/stop/(?P<pk>\d+)/$',
        StopVoting.as_view(),
        name="votecollector_voting_stop"),

    url(r'^votecollector/votingstatus/$',
        GetStatus.as_view(),
        name="votecollector_voting_status"),

    url(r'^votecollector/votingstatus/(?P<pk>\d+)/$',
        GetVotingStatus.as_view(),
        name="votecollector_voting_status"),

    url(r'^votecollector/votingresults/$',
        GetVotingResults.as_view(),
        name="votecollector_voting_results"),
)
