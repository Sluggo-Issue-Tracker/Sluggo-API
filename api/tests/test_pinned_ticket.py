from .test_base import *

class PinnedTicketTestCase(TestCase):
    prefix = "pinned-tickets"
    team_dict = {"name": "bugslotics"}

    user_of_interest_dict = dict(
        username="org.mungus.a",
        email="a@mungus.org",
        first_name="Adam",
        last_name="Mungus",
    )

    member_of_interest_dict = dict(
        role="AD",
        bio="Is not sus"
    )

    user_not_of_interest_dict = dict(
        username="org.mungus.impostor",
        email="impostor@mungus.org",
        first_name="Sus",
        last_name="Mungus"
    )

    member_not_of_interest_dict = dict(
        role="AD",
        bio="Sus!"
    )

    ticket_of_interest_dict = dict(
        title="Ticket Of Interest",
        description="This is a ticket of interest to us."
    )

    ticket_not_of_interest_dict = dict(
        title="Ticket not of Interest",
        description="Please ignore this!"
    )

    def setUp(self):
        # create team
        self.team = Team.objects.create(**self.team_dict)

        # setup users
        self.user_of_interest = User.objects.create(**self.user_of_interest_dict)
        self.user_not_of_interest = User.objects.create(**self.user_not_of_interest_dict)

        # setup members
        self.member_of_interest = Member.objects.create(**self.member_of_interest_dict,
                                                        owner=self.user_of_interest, team=self.team)
        self.member_not_of_interest = Member.objects.create(**self.member_not_of_interest_dict,
                                                            owner=self.user_not_of_interest, team=self.team)
        # setup clients
        self.client_of_interest = APIClient()
        self.client_of_interest.force_authenticate(user=self.user_of_interest)

        self.client_not_of_interest = APIClient()
        self.client_not_of_interest.force_authenticate(user=self.user_not_of_interest)

        self.ticket_of_interest = Ticket.objects.create(**self.ticket_of_interest_dict, team=self.team)

        self.ticket_not_of_interest = Ticket.objects.create(**self.ticket_not_of_interest_dict, team=self.team)

    def test_ticket_pin(self):
        response = self.client_of_interest.post(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            data=dict(
                ticket=self.ticket_of_interest.pk
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if accessible from a GET request
        response = self.client_of_interest.get(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check if holds correct ticket
        self.assertEqual(response.data[0].get('ticket').get('id'), self.ticket_of_interest.pk)

    def test_ticket_unpin_removes_access(self):
        response = self.client_of_interest.post(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            data=dict(
                ticket=self.ticket_of_interest.pk
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pinned_pk = response.data.get('id')

        # Now unpin
        response = self.client_of_interest.delete(
            reverse('pinned-tickets-detail', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk,
                                                     'pk': pinned_pk}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if accessible from a GET request
        response = self.client_of_interest.get(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_ticket_pin_does_not_cross_users(self):
        response = self.client_of_interest.post(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            data=dict(
                ticket=self.ticket_of_interest.pk
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pinned_pk = response.data.get('id')

        response = self.client_not_of_interest.get(
            reverse('pinned-tickets-list',
                    kwargs={'team_pk': self.team.id, 'member_pk': self.member_not_of_interest.pk}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
