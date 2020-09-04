from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Ticket, Team, Member

import datetime

User = get_user_model()

user_dict = dict(email="adam@sicmundus.org", first_name="Jonas", last_name="Kahnwald")

admin_dict = dict(email="Claudia@wnpp.gov", first_name="Claudia", last_name="Tiedemann")

"""
each test validates basic CRUD functionality
"""


class TeamBaseBehavior(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(**user_dict)

    def testTeamCreate(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        team_data = {
            "name": "bugslotics",
            "description": "a very cool team",
            "ticket_head": 0
        }

        response = client.post(
            reverse("team-list"), team_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testTeamRead(self):
        pass

    def testTeamUpdate(self):
        pass

    def testTeamDelete(self):
        pass


class ProfileBaseBehavior(TestCase):

    def setUp(self):
        profile_user = User.objects.create_user(**user_dict)

    def testRead(self):
        # read the record created in setUp. confirm the results are expected
        pass

    def testCreate(self):
        # create a new record. this call should return the newly created record
        pass

    def testUpdate(self):
        # change the record's values. this call should return the newly updated record
        pass

    def testDelete(self):
        pass
