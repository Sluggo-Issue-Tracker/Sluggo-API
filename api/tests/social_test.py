from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Team, Member
from ..serializers import TeamSerializer

import datetime

User = get_user_model()

user_dict = dict(email="adam@sicmundus.org", first_name="Jonas", last_name="Kahnwald")

admin_dict = dict(email="Claudia@wnpp.gov", first_name="Claudia", last_name="Tiedemann")

team_dict = {
    "name": "bugslotics",
    "description": "a pretty cool team"
}

"""
each test validates basic CRUD functionality
"""


class TeamBaseBehavior(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(**user_dict)

        self.team_data = {
            "name": "bugslotics",
            "description": "a very cool team",
            "ticket_head": 0
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.client = client

        response = client.post(
            reverse("team-list"), self.team_data, format="json"
        )

        for k, v in self.team_data.items():
            self.assertEqual(v, response.data.get(k))

        serializer = TeamSerializer(data=response.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        self.team_id = team.id

    def testTeamCreate(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            reverse("team-list"), self.team_data, format="json"
        )

        for k, v in self.team_data.items():
            self.assertEqual(v, response.data.get(k))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testTeamRead(self):

        response = self.client.get(
            reverse("team-detail", kwargs={'pk': self.team_id}), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in self.team_data.items():
            self.assertEqual(v, response.data.get(k))

    def testTeamUpdate(self):

        updated_data = {
            "name": "slugbotics",
            "description": "a very cool team"
        }

        response = self.client.put(
            reverse("team-detail", kwargs={'pk': self.team_id}),
            updated_data,
            format="json"
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in updated_data.items():
            self.assertEqual(v, response.data.get(k))

    def testTeamDelete(self):

        # TODO: 9/5/2020 tdimhcsleumas delete should simply set deactivated rather then deleting the entire record
        #                this will be depended on overriding the delete method, whenever we get to that

        old_count = Team.objects.count()

        response = self.client.delete(
            reverse("team-detail", kwargs={"pk": self.team_id})
        )

        print(response)

        new_count = Team.objects.count()

        self.assertGreater(old_count, new_count)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MemberBaseBehavior(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(**user_dict)
        self.user.save()

        self.team = Team(**team_dict)
        self.team.save()

        self.member_data = {
            "user_id": self.user.id,
            "team_id": self.team.id,
            "role": "AD",
            "bio": "cool dude"
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.client = client

        response = client.post(
            reverse("team-list"), self.member_data, format="json"
        )

        for k, v in self.member_data.items():
            self.assertEqual(v, response.data.get(k))

        serializer = TeamSerializer(data=response.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        self.member_id = member.id

    def testMemberCreate(self):
        # create a new record. this call should return the newly created record
        pass


    def testMemberRead(self):
        # read the record created in setUp. confirm the results are expected
        pass

    def testMemberUpdate(self):
        # change the record's values. this call should return the newly updated record
        pass

    def testMemberApproval(self):
        pass

    def testMemberDelete(self):
        pass
