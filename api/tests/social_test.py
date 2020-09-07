from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Team, Member
from ..serializers import TeamSerializer, MemberSerializer

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
        self.team = Team.objects.create(**team_dict)
        self.team.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def testTeamCreate(self):

        team_data = {
            "name": "slugbotics",
            "description": "a medium cool team"
        }

        response = self.client.post(
            reverse("team-list"), team_data, format="json"
        )

        for k, v in team_data.items():
            self.assertEqual(v, response.data.get(k))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testTeamRead(self):

        response = self.client.get(
            reverse("team-detail", kwargs={'pk': self.team.id}), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in team_dict.items():
            self.assertEqual(v, response.data.get(k))

    def testTeamUpdate(self):

        updated_data = {
            "description": "a very cool team"
        }

        response = self.client.put(
            reverse("team-detail", kwargs={'pk': self.team.id}),
            updated_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in updated_data.items():
            self.assertEqual(v, response.data.get(k))

    def testTeamDelete(self):

        old_count = Team.objects.count()

        response = self.client.delete(
            reverse("team-detail", kwargs={"pk": self.team.id})
        )

        new_count = Team.objects.count()

        self.assertGreater(old_count, new_count)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MemberBaseBehavior(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(**user_dict)
        self.user.save()

        self.team = Team.objects.create(**team_dict)
        self.team.save()

        self.member_data = {
            "team_id": self.team.id,
            "role": "AD",
            "bio": "cool dude"
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.client = client

        response = client.post(
            reverse("member-list"), self.member_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for k, v in self.member_data.items():
            self.assertEqual(v, response.data.get(k))

        self.member_id = response.data["id"]

    def testMemberCreate(self):
        # create a new record. this call should return the newly created record
        record = Member.objects.get(id=1)
        self.assertEqual(Member.objects.count(), 1)

    def testMemberRead(self):
        # read the record created in setUp. confirm the results are expected
        response = self.client.get(
            reverse("member-detail", kwargs={'pk': self.member_id}), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in self.member_data.items():
            self.assertEqual(v, response.data.get(k))

    def testMemberUpdate(self):
        # change the record's values. this call should return the newly updated record
        new_data = {
            "bio": "no longer a cool dude"
        }

        response = self.client.put(
            reverse("member-detail", kwargs={'pk': self.member_id}),
            new_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in new_data.items():
            self.assertEqual(v, response.data.get(k))

    def testMemberApproval(self):
        pass

    def testMemberDelete(self):
        # i might consider using the deactivated fields here in order to revoke / re-enable requests
        # althought hard deletion may be okay for this
        old_count = Member.objects.count()

        response = self.client.delete(
            reverse("member-detail", kwargs={"pk": self.member_id})
        )

        new_count = Member.objects.count()

        self.assertGreater(old_count, new_count)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


