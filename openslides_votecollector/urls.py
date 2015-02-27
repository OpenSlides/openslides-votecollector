# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import (Overview, KeypadCreate, KeypadUpdate, StatusView,
                    StartVoting, StopVoting, GetVotingResults, GetVotingStatus,
                    GetStatus, KeypadDelete, KeypadCreateMulti, MakeAnonymousView,
                    MotionDetailView, MotionPollDetailView, MotionPollDetailPDFView)

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
        name="votecollector_voting_status"),  # TODO

    url(r'^votecollector/votingstatus/(?P<pk>\d+)/$',
        GetVotingStatus.as_view(),
        name="votecollector_voting_status"),  # TODO

    url(r'^votecollector/votingresults/$',
        GetVotingResults.as_view(),
        name="votecollector_voting_results"),

    # Motion
    url(r'^motion/(?P<pk>\d+)/$',
        MotionDetailView.as_view(),
        name='motion_detail'),
    url(r'^motion/(?P<pk>\d+)/poll/(?P<poll_number>\d+)/$',
        MotionPollDetailView.as_view(),
        name='motionpoll_detail'),
    url(r'^motion/(?P<pk>\d+)/poll/(?P<poll_number>\d+)/resultpdf/$',
        MotionPollDetailPDFView.as_view(),
        name='motionpoll_detail_pdf'),
    url(r'^motion/(?P<pk>\d+)/poll/(?P<poll_number>\d+)/make-anonymous/$',
        MakeAnonymousView.as_view(),
        name="votecollector_make_anonymous"),
)
