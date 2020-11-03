from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Team, Member
from ..views import MemberViewSet
from ..serializers import TeamSerializer, MemberSerializer

import datetime

User = get_user_model()

user_dict = dict(
    username="org.sicmundus.adam",
    email="adam@sicmundus.org",
    first_name="Jonas",
    last_name="Kahnwald",
)

admin_dict = dict(
    username="gov.wnpp.Claudia",
    email="Claudia@wnpp.gov",
    first_name="Claudia",
    last_name="Tiedemann",
)

team_dict = {"name": "bugslotics", "description": "a pretty cool team"}

"""
each test validates basic CRUD functionality
"""


class TeamBaseBehavior(TestCase):
    def setUp(self):
        self.client = APIClient()

        response = self.client.post(
            reverse("rest_register"),
            {
                "username": "sschmidt",
                "password1": "p@ssw0rd90",
                "password2": "p@ssw0rd90",
                "email": "sadschmi@test.com",
            },
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data.get("key"))

        # if team creation fails, then all other tests will fail

        response = self.client.post(
            reverse("team-create-record"),
            team_dict,
            format="json"
        )

        for k, v in team_dict.items():
            self.assertEqual(v, response.data.get(k))

        self.team = Team.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(User.objects.count(), 0)

    def testTeamRead(self):

        response = self.client.get(
            reverse("team-detail", kwargs={"pk": self.team.id}), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in team_dict.items():
            self.assertEqual(v, response.data.get(k))

    def testTeamUpdate(self):

        updated_data = {"description": "a very cool team"}

        response = self.client.put(
            reverse("team-detail", kwargs={"pk": self.team.id}),
            updated_data,
            format="json",
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
        print(response.data)

        self.assertGreater(old_count, new_count)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def testTeamSearch(self):
        response = self.client.get(
            reverse("team-search", kwargs={"q": "bugslotics a very cool team"})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MemberBaseBehavior(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(**user_dict)
        self.user.save()

        self.team = Team.objects.create(**team_dict)
        self.team.save()

        self.member_data = {"team_id": self.team.id, "role": "AD", "bio": "cool dude"}

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.client = client

        response = client.post(
            reverse("member-create-record"), self.member_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for k, v in self.member_data.items():
            self.assertEqual(v, response.data.get(k))

        self.member_id = response.data["id"]

    def testMemberCreate(self):
        # create a new record. this call should return the newly created record
        record = Member.objects.get(id=self.member_id)
        self.assertEqual(Member.objects.count(), 1)

    def testMemberRead(self):
        # read the record created in setUp. confirm the results are expected
        response = self.client.get(
            reverse("member-detail", kwargs={"pk": self.member_id}), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for k, v in self.member_data.items():
            self.assertEqual(v, response.data.get(k))

    def testMemberUpdate(self):
        # change the record's values. this call should return the newly updated record
        new_data = {
            "bio": "no longer a cool dude",
            "user": {"first_name": "Robert", "last_name": "Sutton"},
        }

        response = self.client.put(
            reverse("member-detail", kwargs={"pk": self.member_id}),
            new_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testMemberApproval(self):

        response = self.client.patch(
            reverse("member-approve", kwargs={"pk": self.member_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testMemberDelete(self):

        response = self.client.patch(
            reverse("member-leave", kwargs={"pk": self.member_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UnauthenticatedBehavior(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**user_dict)
        self.user.save()

        self.team = Team.objects.create(**team_dict)
        self.team.save()

        self.member_data = {"team_id": self.team.id, "role": "AD", "bio": "cool dude"}

        self.client = APIClient()

        response = self.client.post(
            reverse("member-list"), self.member_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testUnauthenticated(self):
        pass

