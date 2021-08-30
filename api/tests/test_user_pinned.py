from unittest import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..serializers import TicketSerializer
from .test_base import User, generateArbitraryTeams, generateArbitraryTickets

test_user = dict(
    username="gov.wnpp.Claudia",
    email="Claudia@wnpp.gov",
    first_name="Claudia",
    last_name="Tiedemann",
)


class TestUserPinnedTickets(TestCase):
    prefix = "user-pinned-tickets"

    def testGetsUserAssignedTickets(self):
        # create necessary data
        user = User.objects.create(**test_user)
        teams = generateArbitraryTeams(3)

        # create some pinned tickets
        pinned_tickets = generateArbitraryTickets(teams, 3, assignee=user, pinned=True)

        # create some unpinned tickets
        generateArbitraryTickets(teams, 5)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(reverse(self.prefix + "-list"))

        # response should only include the pinned tickets
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, TicketSerializer(pinned_tickets, many=True).data
        )
