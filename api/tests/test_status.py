from .test_base import *


class StatusTestCase(TeamRelatedCore):
    prefix = "team-statuses"
    model = TicketStatus
    serializer = TicketStatusSerializer

    data_dict = {"title": "in progress", "color": "#F5F225FF"}

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
        updated_dict = dict(self.data_dict)
        updated_dict["title"] = "alsdkfj"
        updated_dict["color"] = "#F39617FF"

        expected = self.serializer(self.model.objects.get(pk=self.pk)).data
        expected["title"] = updated_dict["title"]
        expected["color"] = updated_dict["color"]
        self.update(updated_dict, expected)

    def testBadColor(self):
        updated_dict = dict(self.data_dict)
        updated_dict["color"] = "bad"

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.put(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            data=updated_dict,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)

    def testDelete(self):
        self.delete()
