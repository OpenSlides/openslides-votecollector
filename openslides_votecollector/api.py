# -*- coding: utf-8 -*-

import json

from xmlrpclib import ServerProxy

from django.db import transaction
from django.utils.translation import ugettext as _

from openslides.config.api import config
from openslides.projector.api import update_projector

from .models import Keypad, MotionPollKeypadConnection


VOTECOLLECTOR_ERROR_MESSAGES = {
    -1: _('Unknown voting mode.'),
    -2: _('Invalid keypad range.'),
    -3: _('Invalid keypad list.'),
    -4: _('No keypads authorized for voting.'),
    -5: _('License not sufficient.'),
    -6: _('No voting device connected.'),
    -7: _('Failed to set up voting device.'),
    -8: _('Voting device not ready.'),
}

# For cert authentification see:
# http://mail.python.org/pipermail/python-list/2010-January/1231391.html


class VoteCollectorError(Exception):
    """
    Error class for the VoteCollector Plugin
    """
    def __init__(self, value=None, nr=None):
        if nr is not None:
            self.value = VOTECOLLECTOR_ERROR_MESSAGES[nr]
        elif value is not None:
            self.value = value
        else:
            self.value = ''

    def __str__(self):
        return repr("VoteCollector Exception: %s" % self.value)


def get_server():
    """
    Gets a xmlrpclib.ServerProxy objects and test it, if a connection
    is possible.
    """
    try:
        server = ServerProxy(config['votecollector_uri'])
    except TypeError:
        raise VoteCollectorError(_('Server not found.'))

    # Test the connection
    try:
        server.voteCollector.getDeviceStatus()
    except:
        raise VoteCollectorError(_('No connection to VoteCollector.'))
    else:
        return server


def get_VoteCollector_status():
    """
    Return a status message from the VoteCollector.
    """
    server = get_server()

    return server.voteCollector.getDeviceStatus()


def start_voting(poll_id):
    """
    Stars a voting.

    Returns the number of active keypads.
    """
    if config['votecollector_in_vote']:
        return None
    server = get_server()
    keypads = Keypad.objects.exclude(user__is_active=False) \
                    .values_list('keypad_id', flat=True).order_by('keypad_id')

    if config['votecollector_method'] == 'anonym':
        keypads = keypads.filter(user=None)
    elif config['votecollector_method'] == 'person':
        keypads = keypads.exclude(user=None)

    if not keypads.exists():
        raise VoteCollectorError(_('No keypads selected.'))

    # TODO: Check the api using a keypad list or arrays of ids, see VoteCollector 1.4.x Changelog
    count_prepare = server.voteCollector.prepareVoting('YesNoAbstain', 0, 0, list(keypads))
    if count_prepare < 0:
        raise VoteCollectorError(nr=count_prepare)

    count = server.voteCollector.startVoting()
    if count < 0:
        raise VoteCollectorError(nr=count)

    config['votecollector_in_vote'] = poll_id
    config['votecollector_active_keypads'] = count
    return count


def stop_voting():
    """
    Stops the voting.

    Return None if no vote was
    """
    if not config['votecollector_in_vote']:
        return None
    server = get_server()
    server.voteCollector.stopVoting()
    config['votecollector_in_vote'] = 0
    return True


def get_voting_status():
    """
    Return a list. The first element is the seconds since the vote was startet,
    the second element are the number of keypads allready voted.
    """
    server = get_server()
    status = server.voteCollector.getVotingStatus()
    return status


def get_voting_results():
    """
    return the results of the last vote.
    """
    server = get_server()
    return server.voteCollector.getVotingResult()


def update_personal_votes(poll):
    """
    Loads all personal vote results and saves them into the database.
    """
    server = get_server()
    votelog_json = server.voteCollector.getVoteLog()
    votelog = json.loads(votelog_json)
    keypad_dict = {}
    for keypad in Keypad.objects.all():
        # Be careful: Don't mix up keypad.pk and keypad_id. It is tricky.
        keypad_dict[keypad.keypad_id] = keypad.pk
    with transaction.atomic():
        MotionPollKeypadConnection.objects.filter(poll=poll).delete()
        connection_objects = []
        for item in votelog:
            if item['value'] not in ('Y', 'N', 'A'):
                raise VoteCollectorError(nr=-1)  # TODO: Check this.
            connection_objects.append(MotionPollKeypadConnection(
                poll=poll,
                keypad_id=keypad_dict[int(item['id'])],
                value=item['value'],
                serial_number=item['sn']))
        MotionPollKeypadConnection.objects.bulk_create(connection_objects)
    update_projector()  # TODO: Only update when motion poll slide is active
