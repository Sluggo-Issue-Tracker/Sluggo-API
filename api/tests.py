from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()

assigned_dict = dict(email="noah@sicmundus.org", first_name="Hanno", last_name="Tauber")

user_dict = dict(email="adam@sicmundus.org", first_name="Jonas", last_name="Kahnwald")

admin_dict = dict(email="Claudia@wnpp.gov", first_name="Claudia", last_name="Tiedemann")


import datetime

from .models import Ticket
from .models import Profile


class TicketTestCase(TestCase):
    """This class defines the test suite for the ticket model"""

    def setUp(self):
        """ Create two test users Jonas and Martha and a ticket assigned to/created from them"""

        ticket_user = User.objects.create_user(**user_dict)
        assigned_user = User.objects.create_user(**assigned_dict)

        self.ticket_name = "Testing Ticket"
        self.ticket_description = "Ticket used for testing"

        self.ticket_due = datetime.datetime(2020, 12, 29)

        self.ticket = Ticket(
            owner=ticket_user,
            assigned_user=assigned_user,
            title=self.ticket_name,
            due_date=self.ticket_due,
        )

    def test_model_can_create_ticket(self):
        """ Test whetheher it can create a ticket"""
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

        self.assigned_user = User.objects.create_user(**assigned_dict)
        self.admin_user = User.objects.create_user(**admin_dict)
        self.admin_user.profiles.role = Profile.Roles.ADMIN

        # Create a client with authentication
        self.client = APIClient()
        self.client.force_authenticate(user=self.ticket_user)
        self.ticket_data = {
            "owner": self.ticket_user.id,
            "assigned_user": self.assigned_user.id,
            "title": "Sic Mundus Creatus Est",
            "due_date": None,
        }
        self.response = self.client.post(
            reverse("ticket-list"), self.ticket_data, format="json"
        )

    def test_api_can_create_a_ticket(self):
        """Test if the api can create a ticket."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization"""
        new_client = APIClient()
        self.ticket_data = {
            "owner": self.ticket_user.id,
            "assigned_user": self.assigned_user.id,
            "title": "Sic Mundus Creatus Est",
            "due_date": None,
        }
        res = new_client.post(reverse("ticket-list"), self.ticket_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_get_a_ticket(self):
        """Test the api can get a given ticket."""
        ticket = Ticket.objects.get(id=1)
        response = self.client.get(
            reverse("ticket-detail", kwargs=dict(pk=ticket.id)), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, ticket.title)

    def test_api_auth_can_update_a_ticket(self):
        """ Test that the ticket author can update the ticket"""
        ticket = Ticket.objects.get(id=1)
        change_ticket = dict(
            title="Its happening again",
            owner=self.ticket_user.id,
            assigned_user=self.assigned_user.id,
        )
        res = self.client.put(
            reverse("ticket-detail", kwargs={"pk": ticket.id}),
            change_ticket,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_no_auth_cant_update_ticket(self):
        """ Test that a non signed in user can't edit the ticket"""
        ticket = Ticket.objects.get(id=1)
        change_ticket = dict(
            title="Its happening again",
            owner=self.ticket_user.id,
            assigned_user=self.assigned_user.id,
        )
        new_client = APIClient()
        res = new_client.put(
            reverse("ticket-detail", kwargs={"pk": ticket.id}),
            change_ticket,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_not_owner_cant_update_ticket(self):
        """ Test that only the owner can edit tickets""""
        ticket = Ticket.objects.get(id=1)
        change_ticket = dict(
            title="Its happening again",
            owner=self.ticket_user.id,
            assigned_user=self.assigned_user.id,
        )
        new_client = APIClient()
        new_client.force_authenticate(user=self.assigned_user)
        res = new_client.put(
            reverse("ticket-detail", kwargs={"pk": ticket.id}),
            change_ticket,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_admin_can_update_ticket(self):
        """ Test that admins have override ability to edit tickets"""
        ticket = Ticket.objects.get(id=1)
        change_ticket = dict(
            title="Its happening again",
            owner=self.ticket_user.id,
            assigned_user=self.assigned_user.id,
        )
        new_client = APIClient()
        new_client.force_authenticate(user=self.admin_user)
        res = new_client.put(
            reverse("ticket-detail", kwargs={"pk": ticket.id}),
            change_ticket,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_auth_can_delete_a_ticket(self):
        """ Test that owner/properly authenticated user can delete the ticket"""
        ticket = Ticket.objects.get(id=1)
        res = self.client.delete(
            reverse("ticket-detail", kwargs={"pk": ticket.id}),
            format="json",
            follow=True,
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
