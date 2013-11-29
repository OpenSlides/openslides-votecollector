# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import (Overview, KeypadCreate, KeypadUpdate, StatusView,
                    StartVoting, StopVoting, GetVotingResults, GetVotingStatus,
                    GetStatus, KeypadDelete, KeypadSetStatusView, KeypadCreateMulti)

urlpatterns = patterns(
    '',
    url(r'^$',
        Overview.as_view(),
        name="votecollector_overview"),

    url(r'^new/$',
        KeypadCreate.as_view(),
        name="votecollector_keypad_new"),

    url(r'^new/multi/$',
        KeypadCreateMulti.as_view(),
        name="votecollector_keypad_new_multi"),

    url(r'^(?P<pk>\d+)/edit/',
        KeypadUpdate.as_view(),
        name="votecollector_keypad_edit"),

    url(r'^(?P<pk>\d+)/del/',
        KeypadDelete.as_view(),
        name="votecollector_keypad_delete"),

    url(r'^(?P<pk>\d+)/toggle/$',
        KeypadSetStatusView.as_view(),
        {'action': 'toggle'},
        name='votecollector_keypad_status_toggle'),

    url(r'^(?P<pk>\d+)/activate/',
        KeypadSetStatusView.as_view(),
        {'action': 'activate'},
        name="votecollector_keypad_activate"),

    url(r'^(?P<pk>\d+)/deactivate/',
        KeypadSetStatusView.as_view(),
        {'action': 'deactivate'},
        name="votecollector_keypad_deactivate"),

    url(r'^status/$',
        StatusView.as_view(),
        name="votecollector_status"),

    url(r'^start/(?P<pk>\d+)/$',
        StartVoting.as_view(),
        name="votecollector_voting_start"),

    url(r'^stop/(?P<pk>\d+)/$',
        StopVoting.as_view(),
        name="votecollector_voting_stop"),

    url(r'^votingstatus/$',
        GetStatus.as_view(),
        name="votecollector_voting_status"),

    url(r'^votingstatus/(?P<pk>\d+)/$',
        GetVotingStatus.as_view(),
        name="votecollector_voting_status"),

    url(r'^votingresults/$',
        GetVotingResults.as_view(),
        name="votecollector_voting_results"),
)
