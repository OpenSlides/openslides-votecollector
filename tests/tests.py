# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.test.client import Client

from openslides.participant.models import User
from openslides.utils.test import TestCase


class VoteCollectorView(TestCase):
    """
    Tests the votecollector view.
    """
    def setUp(self):
        perm = Permission.objects.get(codename='can_manage_votecollector')
        self.manager = User.objects.get(pk=1)
        self.manager.user_permissions.add(perm)
        self.normal_user = User.objects.create_user(username='user', password='Ohai4aeyo7can1fahzat')
        self.client_1 = Client()
        self.client_1.login(username='admin', password='admin')
        self.client_2 = Client()
        self.client_2.login(username='user', password='Ohai4aeyo7can1fahzat')

    def test_tab(self):
        response = self.client_1.get('/votecollector/')
        self.assertContains(response, 'Keypads', status_code=200)
        response = self.client_2.get('/votecollector/')
        self.assertNotContains(response, 'Keypads', status_code=403)
