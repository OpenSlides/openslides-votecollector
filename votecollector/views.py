#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.views
    ~~~~~~~~~~~~~~~~~~~

    Views for the VoteCollector Plugin.

    :copyright: 2012-2013 by Oskar Hahn, Emanuel Schütze
    :license: GNU GPL, see LICENSE for more details.
"""

from urllib import urlencode
try:
    from urlparse import parse_qs
except ImportError: # python <= 2.5
    from cgi import parse_qs

# Django imports
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.utils.translation import ugettext as _, ugettext_lazy, ugettext_noop
from django.dispatch import receiver
from django.contrib import messages
from django.template.loader import render_to_string
from django.views.generic.detail import SingleObjectMixin

# OpenSlides imports
from openslides.utils.views import (TemplateView, ListView, UpdateView, CreateView,
    FormView, AjaxView, DeleteView, RedirectView)
from openslides.utils.template import Tab
from openslides.utils.signals import template_manipulation
from openslides.config.api import config
from openslides.motion.models import MotionPoll
#TODO: from openslides.projector.signals import projector_overlays
#from openslides.projector.api import projector_message_set
from openslides.motion.views import PollUpdateView

# VoteCollector imports
from votecollector.models import Keypad
from votecollector.forms import KeypadForm, KeypadMultiForm
from votecollector.api import (start_voting, stop_voting, get_voting_results,
    get_voting_status, VoteCollectorError, get_VoteCollector_status)


class Overview(ListView):
    """
    List all keypads.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/overview.html'
    model = Keypad
    context_object_name = 'keypads'

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)

        # Code for sorting and filtering the keypads
        try:
            sortfilter = parse_qs(self.request.COOKIES['votecollector_sortfilter'])
            for value in sortfilter:
                sortfilter[value] = sortfilter[value][0]
        except KeyError:
            sortfilter = {}

        for value in [u'sort', u'reverse', u'user', u'active']:
            if value in self.request.REQUEST:
                if self.request.REQUEST[value] == '0':
                    try:
                        del sortfilter[value]
                    except KeyError:
                        pass
                else:
                    sortfilter[value] = self.request.REQUEST[value]

        if 'user' in sortfilter:
            if sortfilter['user'] == 'anonymous':
                context['keypads'] = context['keypads'].filter(user=None)
            elif sortfilter['user'] == 'personalized':
                context['keypads'] = context['keypads'].exclude(user=None)
        if 'active' in sortfilter:
            if sortfilter['active'] == 'active':
                context['keypads'] = context['keypads'].filter(active=True)
            elif sortfilter['active'] == 'inactive':
                context['keypads'] = context['keypads'].filter(active=False)

        if 'sort' in sortfilter:
            context['keypads'] = context['keypads'].order_by(sortfilter['sort'])
        else:
            context['keypads'] = context['keypads'].order_by('keypad_id')
        if 'reverse' in sortfilter:
            context['keypads'] = context['keypads'].reverse()

        context['sortfilter'] = sortfilter
        context['cookie'] = ('votecollector_sortfilter', urlencode(sortfilter, doseq=True))

        return context


class KeypadUpdate(UpdateView):
    """
    Updates a keypad.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/edit.html'
    model = Keypad
    context_object_name = 'keypad'
    form_class = KeypadForm
    success_url_name = 'votecollector_overview'


class KeypadCreate(CreateView):
    """
    Creates a new keypad.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/edit.html'
    model = Keypad
    context_object_name = 'keypad'
    form_class = KeypadForm
    success_url_name = 'votecollector_overview'
    apply_url = 'votecollector_keypad_edit'


class KeypadCreateMulti(FormView):
    """
    Creates several keypads.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/new_multi.html'
    form_class = KeypadMultiForm
    success_url_name = 'votecollector_overview'

    def form_valid(self, form):
        for i in range(form.cleaned_data['from_id'], form.cleaned_data['to_id'] + 1):
            try:
                Keypad(keypad_id=i, active=form.cleaned_data['active']).save()
            except IntegrityError:
                messages.info(self.request, _('Keypad %d is already in database.') % i)
        return super(KeypadCreateMulti, self).form_valid(form)


class KeypadDelete(DeleteView):
    """
    Deletes a keypad.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    model = Keypad
    success_url_name = 'votecollector_overview'


class KeypadSetStatusView(SingleObjectMixin, RedirectView):
    """
    Activate or deactivate a keypad.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    # TODO for utils/view.py: use url_name in RedirectView without
    # 'args=self.get_url_name_args()' in reverse(..);
    # workaround: use get_redirect_url instead
    # url_name = 'votecollector_overview'
    allow_ajax = True
    model = Keypad

    def pre_redirect(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = kwargs['action']
        if action == 'activate':
            self.object.active = True
        elif action == 'deactivate':
            self.object.active = False
        elif action == 'toggle':
             self.object.active = not self.object.active
        self.object.save()
        return super(KeypadSetStatusView, self).pre_redirect(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        return reverse('votecollector_overview')

    def get_ajax_context(self, **kwargs):
        context = super(KeypadSetStatusView, self).get_ajax_context(**kwargs)
        context['active'] = self.object.active
        return context


class StatusView(TemplateView):
    """
    Show votecollector status.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/status.html'

    def get_context_data(self, **kwargs):
        context = super(StatusView, self).get_context_data(**kwargs)
        try:
            votecollector_message = get_VoteCollector_status()
        except VoteCollectorError:
            status = _('No connection to the VoteCollector')
            votecollector_message = ''
        else:
            status = _('Connected')
        context['votecollector_status'] = status
        context['votecollector_message'] = votecollector_message
        return context


class VotingView(AjaxView):
    """
    An abstract view for the VoteCollector commands.
    """
    def get_poll(self):
        """
        Return the poll.
        """
        try:
            return MotionPoll.objects.get(pk=self.kwargs['pk']);
        except MotionPoll.DoesNotExist:
            return None

    def test_poll(self):
        """
        Test if there are any problems with the poll.

        Sets self.poll.
        """
        self.poll = self.get_poll()

        if self.poll is None:
            self.error = _('Unknown poll.')
        elif config['votecollector_in_vote'] != self.poll.id and config['votecollector_in_vote']:
            try:
                self.error = _('Another poll is running. <a href="%s">Jump to the active poll.</a>') % \
                    MotionPoll.objects.get(pk=config['votecollector_in_vote']).get_absolute_url()
            except MotionPoll.DoesNotExist:
                config['votecollector_in_vote'] = 0
                self.error = _('Please reload.')
        else:
            self.error = None
            return True
        return False

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


class StartVoting(VotingView):
    """
    Start a polling.
    """
    def get(self, request, *args, **kwargs):
        poll = self.get_poll()

        if poll is None:
            self.error = _('Unknown poll.')
        elif config['votecollector_in_vote'] == poll.id:
            self.error = _('Poll already started.')
        elif config['votecollector_in_vote']:
            self.error = _('Another poll is running.')
        else:
            self.error = None
            try:
                self.result = start_voting(poll.id)
            except VoteCollectorError, err:
                self.error = err.value
            else:
                sid = MotionPoll.objects.get(pk=poll.id).motion.sid
                #TODO: projector_message_set(config['votecollector_please_vote'], sid=sid)
        return super(StartVoting, self).get(request, *args, **kwargs)

    def no_error_context(self):
            return {'count': self.result}


class StopVoting(VotingView):
    """
    Stops a polling.
    """
    def get(self, request, *args, **kwargs):
        if self.test_poll():
            poll = self.get_poll()
            self.result = stop_voting()
            sid = MotionPoll.objects.get(pk=poll.id).motion.sid
            #TODO: projector_message_set(config['votecollector_thank_for_vote'], sid=sid)
        return super(StopVoting, self).get(request, *args, **kwargs)


class GetVotingStatus(VotingView):
    """
    Returns the status of a vote.
    """
    def get(self, request, *args, **kwargs):
        if self.test_poll() and config['votecollector_in_vote']:
            try:
                self.result = get_voting_status()
            except VoteCollectorError, err:
                self.error = str(err.value)
        else:
            self.result = [0, 0]
        return super(GetVotingStatus, self).get(request, *args, **kwargs)

    def no_error_context(self):
        return {
            'count': self.result[1],
            'seconds': self.result[0],
            'active_keypads': config['votecollector_active_keypads'],
            'in_vote': config['votecollector_in_vote'] or False,
        }


class GetStatus(AjaxView):
    """
    Returns the id of the active poll.
    """
    def get_ajax_context(self, **kwargs):
        context = super(GetStatus, self).get_ajax_context(**kwargs)
        context['in_vote'] = config['votecollector_in_vote'] or False
        return context


class GetVotingResults(VotingView):
    """
    Returns the results of the last vote.
    """
    def get(self, request, *args, **kwargs):
        self.error = None
        self.result = get_voting_results()
        return super(GetVotingResults, self).get(request, *args, **kwargs)

    def no_error_context(self):
        return {
            'yes': self.result[0],
            'no': self.result[2],
            'abstain': self.result[1],
            'voted': config['votecollector_active_keypads'] - self.result[3],
        }
        return context


def register_tab(request):
    """
    Set the VoteCollector Tab in OpenSlides
    """
    return Tab(
        title=_('VoteCollector'),
        app='votecollector',
        url=reverse('votecollector_overview'),
        stylefile='styles/votecollector.css',
        permission=request.user.has_perm('votecollector.can_manage_votecollector'),
        selected=request.path.startswith('/votecollector/'),
    )


@receiver(template_manipulation, sender=PollUpdateView, dispatch_uid="votecollector_motion_poll")
def motion_poll_template(sender, **kwargs):
    """
    Alter the motion_poll template to insert the 'StartPolling' button.
    """
    kwargs['context'].update({
        'post_form': render_to_string('votecollector/motion_poll.html'),
    })
    kwargs['context']['extra_javascript'].append('javascript/votecollect.js')
