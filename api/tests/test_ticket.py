from .test_base import *


class TicketTestCase(TeamRelatedCore):
    data_dict = {"title": "ticket", "description": "ticket test"}

    prefix = "team-tickets"
    model = Ticket
    serializer = TicketSerializer

    def setUp(self):
        super().setUp()
        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            data=self.data_dict,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.pk = response.data.get("id")

    def testCreate(self):
        self.create(self.data_dict)

    def testList(self):
        self.list()

    def testDetail(self):
        self.detail()

    def testUpdate(self):
        updated_dict = self.data_dict
        updated_dict["description"] = "alskdjf"

        s_instance = TicketSerializer(self.model.objects.get(pk=self.pk))
        expected = s_instance.data
        expected["description"] = updated_dict["description"]

        self.update(updated_dict, expected)

    def testDelete(self):
        self.delete()

    def testTagOnCreate(self):
        extra_data = dict(self.data_dict)

        ticket_status = TicketStatus.objects.create(title="status", team=self.team)
        extra_data["status"] = ticket_status.id

        tag_instance = Tag.objects.create(title="wine", team=self.team)
        extra_data["tag_list"] = [tag_instance.id]

        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=extra_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testRemoveTagOnUpdate(self):
        tags = [
            Tag.objects.create(title="to be removed", team=self.team),
            Tag.objects.create(title="to be deleted", team=self.team),
        ]
        ticket_instance = Ticket.objects.get(pk=self.pk)
        for tag in tags:
            TicketTag.objects.create(ticket=ticket_instance, team=self.team, tag=tag)

        to_be_kept = Tag.objects.create(title="keep this", team=self.team)
        extra_data = dict(self.data_dict)
        extra_data["tag_list"] = [to_be_kept.pk]
        expected = TicketSerializer(ticket_instance).data
        expected["tag_list"] = [TagSerializer(to_be_kept).data]
        self.update(extra_data, expected)

    def testRemoveAllTags(self):
        tags = [
            Tag.objects.create(title="to be kept", team=self.team),
            Tag.objects.create(title="to be deleted", team=self.team),
        ]
        ticket_instance = Ticket.objects.get(pk=self.pk)
        for tag in tags:
            TicketTag.objects.create(ticket=ticket_instance, team=self.team, tag=tag)

        extra_data = dict(self.data_dict)
        extra_data["tag_list"] = []

        expected = TicketSerializer(ticket_instance).data
        expected["tag_list"] = []
        self.update(extra_data, expected)


class WrongTeamTicketTestCase(TicketTestCase):
    other_user = dict(
        username="org.org.org",
        email="asdf@sicmundus.org",
        first_name="Jonas",
        last_name="Kahnwald",
    )

    def setUp(self):
        super().setUp()

        user_instance = User.objects.create(**self.other_user)
        self.client = APIClient()
        self.client.force_authenticate(user=user_instance)

    # TODO: regularized error messages
    def list(self, expected=None):
        response = self.client.get(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def detail(self, expected=None):
        response = self.client.get(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def update(self, updated_dict, expected=None):
        response = self.client.put(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            data=updated_dict,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def delete(self):
        response = self.client.delete(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testTagOnCreate(self):
        extra_data = dict(self.data_dict)

        ticket_status = TicketStatus.objects.create(title="status", team=self.team)
        extra_data["status"] = ticket_status.id

        tag_instance = Tag.objects.create(title="wine", team=self.team)
        extra_data["tag_list"] = [tag_instance.id]

        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=extra_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
