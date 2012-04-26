#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    votecollector.views
    ~~~~~~~~~~~~~~~~~~~~~~~

    Views for the VoteCollector Plugin.

    :copyright: 2011 by Oskar Hahn.
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
from django.utils.translation import ugettext as _
from django.dispatch import receiver
from django.contrib import messages
from django.template.loader import render_to_string
from django.views.generic.detail import SingleObjectMixin

# OpenSlides imports
from openslides.utils.views import (ListView, UpdateView, CreateView, FormView,
                                    AjaxView, DeleteView, RedirectView)
from openslides.utils.template import Tab
from openslides.utils.signals import template_manipulation
from openslides.config.models import config
from openslides.config.signals import default_config_value
from openslides.application.models import ApplicationPoll
from openslides.projector.signals import projector_overlays
from openslides.projector.api import projector_message_set
from application.views import ViewPoll

# VoteCollector imports
from models import Keypad
from forms import KeypadForm, ConfigForm, KeypadMultiForm
from api import (start_voting, stop_voting, get_voting_results,
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
    success_url = 'votecollector_overview'


class KeypadCreate(CreateView):
    """
    Creates a new keypad.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/edit.html'
    model = Keypad
    context_object_name = 'keypad'
    form_class = KeypadForm
    success_url = 'votecollector_overview'
    apply_url = 'votecollector_keypad_edit'


class KeypadCreateMulti(FormView):
    """
    Creates several keypads.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    template_name = 'votecollector/new_multi.html'
    form_class = KeypadMultiForm
    success_url = 'votecollector_overview'

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
    url = 'votecollector_overview'


class KeypadActivate(RedirectView, SingleObjectMixin):
    """
    Aktivates or deaktivates a keypad.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    url = 'votecollector_overview'
    allow_ajax = True
    model = Keypad

    def pre_redirect(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.active = kwargs['activate']
        self.object.save()
        return super(KeypadActivate, self).pre_redirect(request, *args, **kwargs)

    def get_ajax_context(self, **kwargs):
        context = super(SetActive, self).get_ajax_context(**kwargs)
        context.update({
            'active': kwargs['pk'],
        })
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
            return ApplicationPoll.objects.get(pk=self.kwargs['pk']);
        except ApplicationPoll.DoesNotExist:
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
                    ApplicationPoll.objects.get(pk=config['votecollector_in_vote']).get_absolute_url()
            except ApplicationPoll.DoesNotExist:
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
                sid = ApplicationPoll.objects.get(pk=poll.id).application.sid
                projector_message_set(config['votecollector_please_vote'], sid=sid)
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
            sid = ApplicationPoll.objects.get(pk=poll.id).application.sid
            projector_message_set(config['votecollector_thank_for_vote'], sid=sid)
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


class Config(FormView):
    """
    Config View.
    """
    permission_required = 'votecollector.can_manage_votecollector'
    form_class = ConfigForm
    template_name = 'votecollector/config.html'

    def get_initial(self):
        return {
            'method': config['votecollector_method'],
            'uri': config['votecollector_uri'],
            'please_vote': config['votecollector_please_vote'],
            'thank_for_vote': config['votecollector_thank_for_vote'],
        }

    def form_valid(self, form):
        config['votecollector_method'] = form.cleaned_data['method']
        config['votecollector_uri'] = form.cleaned_data['uri']
        config['votecollector_please_vote'] = form.cleaned_data['please_vote']
        config['votecollector_thank_for_vote'] = form.cleaned_data['thank_for_vote']
        messages.success(self.request, _('VoteCollector settings successfully saved.'))
        return super(Config, self).form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(Config, self).get_context_data(**kwargs)
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


@receiver(default_config_value, dispatch_uid="votecollector_default_config")
def default_config(sender, key, **kwargs):
    """
    Sets the default values for the VoteCollector Plugin.
    """
    return {
        'votecollector_method': 'both',
        'votecollector_uri': 'http://localhost:8030',
        'votecollector_please_vote': _('Please vote!<br>1: Yes | 2: No | 3: Abstain'),
        'votecollector_thank_for_vote': _('Voting finished.<br>Thank you for your vote.'),
        'votecollector_in_vote': 0,
        'votecollector_active_keypads': 0,
    }.get(key)


def register_tab(request):
    """
    Set the VoteCollector Tab in OpenSlides
    """
    selected = request.path.startswith('/votecollector/')
    return Tab(
        title=_('VoteCollector'),
        url=reverse('votecollector_overview'),
        permission=request.user.has_perm('votecollector.can_manage_votecollector'),
        selected=selected,
    )


@receiver(template_manipulation, dispatch_uid='votecollector_submenu')
def set_submenu(sender, request, context, **kwargs):
    """
    Sets the submenü for Keypad page.
    """
    if not request.path.startswith('/votecollector/'):
        return None
    menu_links = [
        (
            reverse('votecollector_overview'),
            _('All keypads'),
            request.path == reverse('votecollector_overview'),
        ),

        (
            reverse('votecollector_keypad_new'),
            _('New keypad'),
            request.path == reverse('votecollector_keypad_new'),
        ),
        (
            reverse('votecollector_keypad_new_multi'),
            _('New keypad range'),
            request.path == reverse('votecollector_keypad_new_multi'),
        ),
    ]

    context.update({
        'menu_links': menu_links,
    })


@receiver(template_manipulation, sender=ViewPoll, dispatch_uid="votecollector_application_poll")
def application_poll_template(sender, **kwargs):
    """
    Alter the application_poll template to insert the 'StartPolling' button.
    """
    kwargs['context'].update({
        'post_form': render_to_string('votecollector/application_poll.html'),
    })
