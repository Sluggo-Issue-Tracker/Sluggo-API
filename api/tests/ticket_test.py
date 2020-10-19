from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Ticket
from ..models import Member
from ..models import Team, Member

import datetime


User = get_user_model()

assigned_dict = dict(
    username="org.sicmundus.noah",
    email="noah@sicmundus.org",
    first_name="Hanno",
    last_name="Tauber",
)

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


class TicketTestCase(TestCase):
    """This class defines the test suite for the ticket model"""

    def setUp(self):
        """ Create two test users Jonas and Noah and a ticket assigned to/created from them"""
        self.ticket_user = User.objects.create_user(**user_dict)
        self.ticket_user.save()

        self.assigned_user = User.objects.create_user(**assigned_dict)
        self.assigned_user.save()

        self.team = Team.objects.create(**team_dict)
        self.team.save()

        self.member_data = {"team_id": self.team.id, "role": "AP", "bio": "Cool Users"}

        self.ticket_client = APIClient()
        self.ticket_client.force_authenticate(user=self.ticket_user)
        response = self.ticket_client.post(
            reverse("member-create-record"), self.member_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.ticket_name = "Testing Ticket"
        self.ticket_description = "Ticket used for testing"

        self.ticket = Ticket(
            owner=self.ticket_user,
            assigned_user=self.assigned_user,
            title=self.ticket_name,
            ticket_number=1,
            team=self.team,
        )

    def test_model_can_create_ticket(self):
        """ Test whether it can create a ticket"""
        old_count = Ticket.objects.count()
        self.ticket.save()
        new_count = Ticket.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_ticket_returns_readable_representation(self):
        """Tests that a readable string is represented for the models instance"""
        self.assertEqual(str(self.ticket), f"Ticket: {self.ticket_name}")


class TicketViewTestCase(TestCase):
    """ Test suite for ticket views."""

    def setUp(self):
        """ Sets up whatever is necessary for views"""
        self.ticket_user = User.objects.create_user(**user_dict)
        self.ticket_user.save()

        self.assigned_user = User.objects.create_user(**assigned_dict)
        self.assigned_user.save()

        self.team = Team.objects.create(**team_dict)
        self.team.save()

        self.member_data = {"team_id": self.team.id, "role": "AP", "bio": "Cool Users"}

        self.admin_data = {"team_id": self.team.id, "role": "AD", "bio": "Cool Users"}

        self.ticket_client = APIClient()
        self.ticket_client.force_authenticate(user=self.ticket_user)
        response = self.ticket_client.post(
            reverse("member-create-record"), self.member_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.ticket_data = {
            # "owner_id": self.ticket_user.id,
            "assigned_user": self.assigned_user,
            "title": "Sic Mundus Creatus Est",
            "ticket_number": 1,
            "team_id": self.team.id,
        }

        self.response = self.ticket_client.post(
            reverse("ticket-list"), self.ticket_data, format="json"
        )
        print(self.response.content)

    def test_api_can_create_a_ticket(self):
        """Test if the api can create a ticket."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization"""
        pass

    def test_api_can_get_a_ticket(self):
        """Test the api can get a given ticket."""
        pass

    def test_api_auth_can_update_a_ticket(self):
        """ Test that the ticket author can update the ticket"""
        pass

    def test_api_no_auth_cant_update_ticket(self):
        """ Test that a non signed in user can't edit the ticket"""
        pass

    def test_api_not_owner_cant_update_ticket(self):
        """ Test that only the owner can edit tickets"""
        pass

    def test_api_admin_can_update_ticket(self):
        """ Test that admins have override ability to edit tickets"""
        pass

    def test_api_auth_can_delete_a_ticket(self):
        """ Test that owner/properly authenticated user can delete the ticket"""
        pass
