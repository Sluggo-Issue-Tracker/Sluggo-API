import string
import random

from .test_base import *
from ..models import *
from ..serializers import *


class TestTeamInvite(TeamRelatedCore):
    prefix = "team-invites"

    def tearDown(self) -> None:
        # delete all entries! (in the test db)
        TeamInvite.objects.all().delete()
        User.objects.all().delete()

    def testCreate(self):
        user = generateArbitraryUsers(1)[0]
        request = dict(user_email=user.email)
        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        pk = response.data.get("id", None)
        self.assertIsNotNone(pk)

        instance = TeamInvite.objects.get(pk=pk)
        self.assertEqual(response.data, TeamInviteSerializer(instance).data)

    # create a bunch of users. do we get them back?
    def testList(self):
        amount = 100
        user_list = generateArbitraryUsers(amount)
        invites = [
            TeamInvite.objects.create(team=self.team, user=user) for user in user_list
        ]

        for itr in range(amount // PAGE_SIZE):
            page = itr + 1
            base_url = reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id})
            url = f"{base_url}?page={page}"
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get("count"), amount)

            serialized_user_list = TeamInviteSerializer(invites, many=True).data

            idx = itr * PAGE_SIZE
            self.assertEqual(
                response.data.get("results"),
                serialized_user_list[idx : idx + PAGE_SIZE],
            )

    def testDelete(self):
        user = generateArbitraryUsers(1)[0]
        instance = TeamInvite.objects.create(user=user, team=self.team)

        response = self.client.delete(
            reverse(
                self.prefix + "-detail",
                kwargs={"team_pk": self.team.id, "pk": instance.id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        queryset = TeamInvite.objects.filter(pk=instance.id)
        self.assertEqual(queryset.count(), 0)
