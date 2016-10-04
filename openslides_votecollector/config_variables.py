from django.utils.translation import ugettext_noop

from openslides.core.config import ConfigVariable

def get_config_variables():
    """
    Generator which yields all config variables of this app.

    It has to be evaluated during app loading (see apps.py).
    """
    yield ConfigVariable(
        name='votecollector_method',
        default_value='both',
        input_type='choice',
        label='Distribution method for keypads',
        choices=(
            {'value': 'anonym', 'display_name': 'Use anonymous keypads only'},
            {'value': 'person', 'display_name': 'Use personalized keypads only'},
            {'value': 'both', 'display_name': 'Use anonymous and personalized keypads'}),
        weight=610,
        group='VoteCollector'
    )
    yield ConfigVariable(
        # TODO: Use URL validator.
        name='votecollector_uri',
        default_value='http://localhost:8030',
        label='URL of VoteCollector',
        help_text='Example: http://localhost:8030',
        weight=620,
        group='VoteCollector'
    )
    yield ConfigVariable(
        name='votecollector_vote_started_msg',
        default_value=ugettext_noop('Please vote now!'),
        label="Overlay message 'Vote started'",
        weight=630,
        group='VoteCollector'
    )
    yield ConfigVariable(
        name='votecollector_live_voting',
        default_value=False,
        input_type='boolean',
        label='Use live voting for motions',
        help_text='Incoming votes will be shown on projector while voting is active.',
        weight=640,
        group='VoteCollector'
    )
    yield ConfigVariable(
        name='votecollector_seating_plan',
        default_value=True,
        input_type='boolean',
        label='Show seating plan',
        help_text='Incoming votes will be shown in seating plan on projector for keypads with assigned seats.',
        weight=650,
        group='VoteCollector'
    )
    yield ConfigVariable(
        name='votecollector_seats_grey',
        default_value=False,
        input_type='boolean',
        label='Show grey seats on seating plan',
        help_text='Incoming votes will be shown in grey on seating plan. You can see only WHICH seat has voted but not HOW.',
        weight=660,
        group='VoteCollector'
    )
