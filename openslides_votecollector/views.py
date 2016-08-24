import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from openslides.agenda.models import Item, Speaker
from openslides.core.config import config
from openslides.core.exceptions import OpenSlidesError
from openslides.core.models import Projector
from openslides.motions.models import MotionPoll
from openslides.utils import views as utils_views
from openslides.utils.rest_api import ModelViewSet, ReadOnlyModelViewSet, Response, list_route

from .api import (
    get_device_status,
    get_voting_result,
    get_voting_status,
    start_voting,
    stop_voting,
    VoteCollectorError
)
from .access_permissions import (
    KeypadAccessPermissions,
    MotionPollKeypadConnectionAccessPermissions,
    SeatAccessPermissions,
    VoteCollectorAccessPermissions,
)
from .models import Keypad, MotionPollKeypadConnection, Seat, VoteCollector


class AjaxView(utils_views.View):
    """
    View for ajax requests.
    """
    required_permission = None

    def check_permission(self, request, *args, **kwargs):
        """
        Checks if the user has the required permission.
        """
        if self.required_permission is None:
            return True
        else:
            return request.user.has_perm(self.required_permission)

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user has the permission.

        If the user is not logged in, redirect the user to the login page.
        """
        if not self.check_permission(request, *args, **kwargs):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_ajax_context(self, **kwargs):
        """
        Returns a dictonary with the context for the ajax response.
        """
        return kwargs

    def ajax_get(self, request, *args, **kwargs):
        """
        Returns the HttpResponse.
        """
        return HttpResponse(json.dumps(self.get_ajax_context()))

    def get(self, request, *args, **kwargs):
        # TODO: Raise an error, if the request is not an ajax-request
        return self.ajax_get(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class VotecollectorViewSet(ModelViewSet):
    access_permissions = VoteCollectorAccessPermissions()
    http_method_names = ['get', 'head', 'options']
    queryset = VoteCollector.objects.all()

    def check_view_permissions(self):
        return self.request.user.has_perm('openslides_votecollector.can_manage_votecollector')


class SeatViewSet(ModelViewSet):
    access_permissions = SeatAccessPermissions()
    queryset = Seat.objects.all()

    def check_view_permissions(self):
        return self.get_access_permissions().can_retrieve(self.request.user)


class KeypadViewSet(ModelViewSet):
    access_permissions = KeypadAccessPermissions()
    queryset = Keypad.objects.all()

    def check_view_permissions(self):
        return self.get_access_permissions().can_retrieve(self.request.user)


class MotionPollKeypadConnectionViewSet(ReadOnlyModelViewSet):
    access_permissions = MotionPollKeypadConnectionAccessPermissions()
    queryset = MotionPollKeypadConnection.objects.all()

    def check_view_permissions(self):
        return self.get_access_permissions().can_retrieve(self.request.user)

    @list_route(methods=['post'])
    def anonymize_votes(self, request):
        """
        Anonymize all votes of the given poll.
        """
        MotionPollKeypadConnection.objects.filter(poll_id=request.data.get('poll_id')).update(keypad=None)
        # TODO: Trigger autoupdate.
        return Response({'detail': _('All votes are successfully anonymized.')})


class VotingView(AjaxView):
    """
    An abstract view for the VoteCollector commands.
    """
    resource_path = '/votecollector'
    voting_key = 'a016f7ecaf2147b2b656c6edf45c24ef'

    def get_callback_url(self, request):
        host = request.META['SERVER_NAME']
        port = request.META.get('SERVER_PORT', 0)
        if port:
            return 'http://%s:%d%s' % (host, port, self.resource_path)
        else:
            return 'http://%s%s' % (host, self.resource_path)

    def get_poll_or_item(self):
        obj = None
        self.error = None
        poll_id = self.kwargs.get('poll_id')
        if poll_id:
            try:
                obj = MotionPoll.objects.get(id=poll_id)
            except MotionPoll.DoesNotExist:
                self.error = _('Unknown poll.')
        else:
            item_id = self.kwargs.get('item_id')
            if item_id:
                try:
                    obj = Item.objects.get(id=self.kwargs['item_id'])
                except Item.DoesNotExist:
                    self.error = _('Unknown item.')
        return obj

    def get_ajax_context(self, **kwargs):
        """
        Return the value of the called command, or the error-message
        """
        context = super(VotingView, self).get_ajax_context(**kwargs)
        if self.error:
            context['error'] = self.error
        else:
            context.update(self.no_error_context())
        return context

    def no_error_context(self):
        """
        Return a dict for the template-context. Called if no errors occurred.
        """
        return {}


class DeviceStatus(VotingView):
    def get(self, request, *args, **kwargs):
        self.error = None
        try:
            self.result = get_device_status()
        except VoteCollectorError as e:
            self.error = e.value
        return super(DeviceStatus, self).get(request, *args, **kwargs)

    def no_error_context(self):
        return {
            'device': self.result,
            'connected': not self.result.startswith('Device: None')
        }


class StartVoting(VotingView):
    def get(self, request, *args, **kwargs):
        mode = kwargs['mode']
        resource = kwargs['resource']
        obj = self.get_poll_or_item()
        vc, created = VoteCollector.objects.get_or_create(id=1)
        if not self.error:
            # Stop any active voting no matter what mode.
            if vc.is_voting:
                try:
                    stop_voting()
                except VoteCollectorError as e:
                    pass
            target = obj.id if obj else 0
            url = self.get_callback_url(request) + resource
            if target:
                url += str(target)
            try:
                self.result = start_voting(mode, url)
            except VoteCollectorError as e:
                self.error = e.value
            else:
                vc.voting_mode = mode
                vc.voting_target = target
                vc.voters_count = self.result
                vc.votes_received = 0
                vc.is_voting = True
                vc.save()
                self.on_start(obj)
        return super(StartVoting, self).get(request, *args, **kwargs)

    def on_start(self, obj):
        pass

    def no_error_context(self):
        return {'count': self.result}


class StartYNA(StartVoting):
    def on_start(self, poll):
        # Clear poll results.
        poll.get_votes().delete()

        # Show voting prompt on projector.
        projector = Projector.objects.get(id=1)
        projector.config[self.voting_key] = {
            'name': 'voting/prompt',
            'message': config['votecollector_vote_started_msg'] +
                "<br>" +
                "<span class='nobr'><img src='/static/img/button-yes.png'> <translate>Yes</translate></span> &nbsp; " +
                "<span class='nobr'><img src='/static/img/button-no.png'> <translate>No</translate></span> &nbsp; " +
                "<span class='nobr'><img src='/static/img/button-abstain.png'> <translate>Abstain</translate></span>",
            'visible': True,
            'stable': True
        }
        projector.save()


class StartSpeakerList(StartVoting):
    def on_start(self, item):
        # Show voting icon on projector.
        projector = Projector.objects.get(id=1)
        projector.config[self.voting_key] = {
            'name': 'voting/icon',
            'stable': True
        }
        projector.save()


class StartPing(StartVoting):
    def on_start(self, obj):
        # Clear in_range and battery_level of all keypads.
        # Attention: Cannot use Keypad.objects.all().update(in_range=False, battery_level=-1)
        # since no post_save signals will be sent on update.
        for keypad in Keypad.objects.all():
            keypad.in_range = False
            keypad.battery_level = -1
            keypad.save()


class StopVoting(VotingView):
    def get(self, request, *args, **kwargs):
        self.error = None

        # Remove voting prompt from projector.
        projector = Projector.objects.get(id=1)
        try:
            del projector.config[self.voting_key]
        except KeyError:
            pass
        else:
            projector.save()

        try:
            self.result = stop_voting()
        except VoteCollectorError as e:
            self.error = e.value
        # Attention: We purposely set is_voting to False even if stop_voting fails.
        vc = VoteCollector.objects.get(id=1)
        vc.is_voting = False
        vc.save()
        return super(StopVoting, self).get(request, *args, **kwargs)


class VotingStatus(VotingView):
    def get(self, request, *args, **kwargs):
        obj = self.get_poll_or_item()
        if not self.error:
            try:
                self.result = get_voting_status()
            except VoteCollectorError as e:
                self.error = e.value
        return super(VotingStatus, self).get(request, *args, **kwargs)

    def no_error_context(self):
        import time
        return {
            'elapsed': time.strftime('%M:%S', time.gmtime(self.result[0])),
            'votes_received': self.result[1]
        }


class ResultYNA(VotingView):
    def get(self, request, *args, **kwargs):
        poll = self.get_poll_or_item()
        if not self.error:
            vc = VoteCollector.objects.get(id=1)
            if vc.voting_mode == 'YesNoAbstain' and vc.voting_target == poll.id:
                try:
                    self.result = get_voting_result()
                except VoteCollectorError as e:
                    self.error = e.value
            else:
                self.error = _('Another voting is active.')
        return super(ResultYNA, self).get(request, *args, **kwargs)

    def no_error_context(self):
        return {
            'yes': self.result[0],
            'no': self.result[1],
            'abstain': self.result[2],
            'not_voted': self.result[3]
        }


class VotingCallbackView(utils_views.View):
    http_method_names = ['post']


class VoteCallback(VotingCallbackView):
    def post(self, request, poll_id, keypad_id):
        # TODO: validate REMOTE_HOST to be VoteCollector or use other authentication method

        # TODO: Use transaction here.

        # Validate vote value.
        value = request.POST.get('value')
        if value not in ('Y', 'N', 'A'):
            return HttpResponse()

        # Get motion poll.
        try:
            poll = MotionPoll.objects.get(id=poll_id)
        except MotionPoll.DoesNotExist:
            return HttpResponse()

        # Get keypad.
        try:
            keypad = Keypad.objects.get(keypad_id=keypad_id)
        except Keypad.DoesNotExist:
            return HttpResponse()

        # Mark keypad as in range and update battery level.
        keypad.in_range = True
        keypad.battery_level = request.POST.get('battery', -1)
        keypad.save()

        # Save vote.
        conn, created = MotionPollKeypadConnection.objects.get_or_create(poll=poll, keypad=keypad)
        conn.value = value
        conn.serial_number = request.POST.get('sn')
        conn.save()

        # Update votecollector.
        vc = VoteCollector.objects.get(id=1)
        vc.votes_received = request.POST.get('votes', 0)
        vc.voting_duration = request.POST.get('elapsed', 0)
        vc.save()

        return HttpResponse()


class SpeakerCallback(VotingCallbackView):

    def post(self, request, item_id, keypad_id):
        # TODO: validate REMOTE_HOST to be VoteCollector or use other authentication method

        # Get agenda item.
        try:
            item = Item.objects.get(id=item_id)
        except MotionPoll.DoesNotExist:
            return HttpResponse()

        # TODO: use timestamp to prioritize speakers

        # Get keypad.
        try:
            keypad = Keypad.objects.get(keypad_id=keypad_id)
        except Keypad.DoesNotExist:
            return HttpResponse(_('Not registered'))

        # Mark keypad as in range and update battery level.
        keypad.in_range = True
        keypad.battery_level = request.POST.get('battery', -1)
        keypad.save()

        # Anonymous users cannot be added or removed from the speaker list.
        if keypad.user is None:
            return HttpResponse(_('Unknown'))

        # Add keypad user to the speaker list.
        value = request.POST.get('value')
        if value == 'Y':
            try:
                # Add speaker to "next speakers" if not already on the list (begin_time=None).
                Speaker.objects.add(keypad.user, item)
            except OpenSlidesError:
                # User is already on the speaker list.
                pass
            content = _('Speaking')
        # Remove keypad user from the speaker list.
        elif value == 'N':
            # Remove speaker if on "next speakers" list (begin_time=None, end_time=None).
            Speaker.objects.filter(user=keypad.user, item=item, begin_time=None, end_time=None).delete()
            content = _('Not speaking')
        else:
            content = _('Invalid')
        return HttpResponse(content)


class KeypadCallback(VotingCallbackView):

    def post(self, request, keypad_id):
        # TODO: validate REMOTE_HOST to be VoteCollector or use other authentication method

        # Get keypad.
        try:
            keypad = Keypad.objects.get(keypad_id=keypad_id)
        except Keypad.DoesNotExist:
            return HttpResponse()

        # Mark keypad as in range and update battery level.
        keypad.in_range = True
        keypad.battery_level = request.POST.get('battery', -1)
        keypad.save()
        return HttpResponse()
