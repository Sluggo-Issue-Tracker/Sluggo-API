from .test_base import *


class TeamTestCase(TeamRelatedCore):
    prefix = "team"
    model = Team
    serializer = TeamSerializer

    def testCreate(self):
        count = Team.objects.count()
        self.assertNotEqual(0, count)

    def testList(self):
        response = self.client.get(reverse("team-list"), format="json")
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
            reverse("team-detail", kwargs={"pk": self.team.id}),
            data=updated_team_dict,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDelete(self):
        response = self.client.delete(
            reverse("team-detail", kwargs={"pk": self.team.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def testMultipleListed(self):
        other_team = {"name": "!alksdjf"}
        response = self.client.post(reverse("team-list"), other_team, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse("team-list"), format="json")
        expected = TeamSerializer(
            Team.objects.filter(member__owner=self.user), many=True
        ).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
