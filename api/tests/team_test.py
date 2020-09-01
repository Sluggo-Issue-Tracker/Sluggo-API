from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Ticket
from ..models import Profile

import datetime

User = get_user_model()

assigned_dict = dict(email="noah@sicmundus.org", first_name="Hanno", last_name="Tauber")

user_dict = dict(email="adam@sicmundus.org", first_name="Jonas", last_name="Kahnwald")

admin_dict = dict(email="Claudia@wnpp.gov", first_name="Claudia", last_name="Tiedemann")


class TeamBaseBehavior(TestCase):
    def setUp(self):
        pass

    def testRead(self):
        # read the record, confirm it serializes correctly
        pass

    def testCreate(self):
        # when we create a team, a member entry should be generated for that user with an admin role
        # on creation, the created record should be returned
        pass

    def testUpdate(self):
        # change the fields. confirm that the updated record is returned
        pass

    def testDelete(self):
        # deactivate the record. confirm that the other fields no longer exist as well
        # probably want to favor deactivation rather than hard deletion
        pass


class TeamMemberBehavior(TestCase):
    def setUp(self):
        pass

    def testJoin(self):
        # join an organization. this should create a member entry with user_id and team_id associated with the user
        # and team, respectively
        pass

    def testLeave(self):
        pass
