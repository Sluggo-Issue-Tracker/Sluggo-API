from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from api.models import (Ticket, Team, Member, Tag, TicketStatus, TicketTag, TicketNode)
from ..serializers import UserSerializer, TicketStatusSerializer, TicketTagSerializer

User = get_user_model()

class TeamRelatedCore(TestCase):
    team_dict = {"name": "bugslotics", "description": "a pretty cool team"}

    member_dict = dict(
        role="AD",
        bio="bio"
    )

    user_dict = dict(
        username="org.sicmundus.adam",
        email="adam@sicmundus.org",
        first_name="Jonas",
        last_name="Kahnwald",
    )

    def setUp(self):
        self.user = User.objects.create(**self.user_dict)
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("team-list"), self.team_dict, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.team = Team.objects.get(pk=1)
        Member.objects.create(team=self.team, owner=self.user, **self.member_dict)


class TeamTestCase(TeamRelatedCore):

    def testCreate(self):
        count = Team.objects.count()
        self.assertNotEqual(0, count)

    def testList(self):
        response = self.client.get(
            reverse("team-list"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDetail(self):
        response = self.client.get(
            reverse("team-detail", kwargs={"pk": self.team.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testUpdate(self):
        updated_team_dict = self.team_dict
        updated_team_dict["description"] = "not cool"
        response = self.client.put(
            reverse("team-detail", kwargs={"pk": self.team.id}), data=updated_team_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDelete(self):
        response = self.client.delete(
            reverse("team-detail", kwargs={"pk": self.team.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TicketTestCase(TeamRelatedCore):

    ticket_dict = {
        "name": "ticket",
        "description": "ticket test"
    }

    def testCreate(self):
        response = self.client.post(
            reverse("team-tickets-list", kwargs={"new_team_pk": self.team.id}),
            data=self.ticket_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testList(self):
        response = self.client.get(
            reverse("team-tickets-list", kwargs={"new_team_pk": self.team.id}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDetail(self):
        response = self.client.get(
            reverse("team-tickets-detail", kwargs={
                "new_team_pk": self.team.id,
                "pk": 1
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testUpdate(self):
        updated_ticket_dict = self.ticket_dict
        updated_ticket_dict["description"] = "alskdjf"
        response = self.client.put(
            reverse("team-tickets-detail", kwargs={
                "new_team_pk": self.team.id,
                "pk": 1
            }), data=updated_ticket_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDelete(self):
        response = self.client.delete(
            reverse("team-tickets-detail", kwargs={
                "new_team_pk": self.team.id,
                "pk": 1
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

