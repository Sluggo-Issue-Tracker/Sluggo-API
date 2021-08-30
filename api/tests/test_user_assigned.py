from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .test_base import User, generateArbitraryTeams, generateArbitraryTickets
from ..serializers import TicketSerializer

test_user = dict(
    username="gov.wnpp.Claudia",
    email="Claudia@wnpp.gov",
    first_name="Claudia",
    last_name="Tiedemann",
)


class TestUserAssignedTickets(TestCase):
    prefix = "user-assigned-tickets"

    def testGetsUserAssignedTickets(self):
        # create necessary data
        user = User.objects.create(**test_user)
        teams = generateArbitraryTeams(3)
        tickets = generateArbitraryTickets(teams, count_per_team=3, assignee=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(reverse(self.prefix + "-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, TicketSerializer(tickets, many=True).data)
