from xmlrpc.client import ServerProxy

from django.utils.translation import ugettext as _

from openslides.core.config import config

from .models import Keypad


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
    Gets a server proxy object and tests the connection.
    """
    try:
        server = ServerProxy(config['votecollector_uri'])
        # TODO: reduce timeout
    except TypeError:
        raise VoteCollectorError(_('Server not found.'))

    # Test the connection
    try:
        server.voteCollector.getDeviceStatus()
    except:
        raise VoteCollectorError(_('No connection to VoteCollector.'))
    else:
        return server


def get_keypads():
    keypads = Keypad.objects.exclude(user__is_active=False).values_list(
        'keypad_id', flat=True).order_by('keypad_id')

    if config['votecollector_method'] == 'anonym':
        keypads = keypads.filter(user=None)
    elif config['votecollector_method'] == 'person':
        keypads = keypads.exclude(user=None)

    if not keypads.exists():
        raise VoteCollectorError(_('No keypads selected.'))

    return keypads


def get_device_status():
    server = get_server()
    return server.voteCollector.getDeviceStatus()


def start_voting(mode, callback_url):
    server = get_server()
    keypads = get_keypads()

    count = server.voteCollector.prepareVoting(mode + '-' + callback_url, 0, 0, list(keypads))
    if count < 0:
        raise VoteCollectorError(nr=count)

    count = server.voteCollector.startVoting()
    if count < 0:
        raise VoteCollectorError(nr=count)

    return count


def stop_voting():
    server = get_server()
    server.voteCollector.stopVoting()
    return True


def get_voting_status():
    """
    Returns voting status as a list: [elapsed_seconds, votes_received]
    """
    server = get_server()
    status = server.voteCollector.getVotingStatus()
    return status


def get_voting_result():
    """
    Returns the voting result as a list.
    """
    server = get_server()
    return server.voteCollector.getVotingResult()
