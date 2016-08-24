from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url(r'^votecollector/device/$',
        views.DeviceStatus.as_view(),
        name='votecollector_device'),

    url(r'^votecollector/start_yna/(?P<poll_id>\d+)/$',
        views.StartYNA.as_view(), {
            'mode': 'YesNoAbstain',
            'resource': '/vote/'
        },
        name='votecollector_start_yna'),

    url(r'^votecollector/start_speaker_list/(?P<item_id>\d+)/$',
        views.StartSpeakerList.as_view(), {
            'mode': 'SpeakerList',
            'resource': '/speaker/'
        },
        name='votecollector_start_speaker_list'),

    url(r'^votecollector/start_ping/$',
        views.StartPing.as_view(), {
            'mode': 'Ping',
            'resource': '/keypad/'
        },
        name='votecollector_start_ping'),

    url(r'^votecollector/stop/$',
        views.StopVoting.as_view(),
        name='votecollector_stop'),

    url(r'^votecollector/status/$',
        views.VotingStatus.as_view(),
        name='votecollector_status'),

    url(r'^votecollector/result_yna/(?P<poll_id>\d+)/$',
        views.ResultYNA.as_view(),
        name='votecollector_result_yna'),

    url(r'^votecollector/vote/(?P<poll_id>\d+)/(?P<keypad_id>\d+)/$',
        csrf_exempt(views.VoteCallback.as_view()),
        name='votecollector_vote'),

    url(r'^votecollector/speaker/(?P<item_id>\d+)/(?P<keypad_id>\d+)/$',
        csrf_exempt(views.SpeakerCallback.as_view()),
        name='votecollector_speaker'),

    url(r'^votecollector/keypad/(?P<keypad_id>\d+)/$',
        csrf_exempt(views.KeypadCallback.as_view()),
        name='votecollector_speaker'),
]
