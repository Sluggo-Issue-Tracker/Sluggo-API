from .test_base import *


class TagTestCase(TeamRelatedCore):
    prefix = "team-tags"
    serializer = TagSerializer

    data_dict = {"title": "wine"}

    model = Tag

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
        updated_dict["title"] = "alsdkfj"

        expected = self.serializer(self.model.objects.get(pk=self.pk)).data
        expected["title"] = updated_dict["title"]

        self.update(updated_dict, expected)

    def testDelete(self):
        self.delete()
