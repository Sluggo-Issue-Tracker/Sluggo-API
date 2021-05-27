import string
import random

from .test_base import *
from ..models import *
from ..serializers import *


class TestUserInvite(TestCase):
    prefix = "user-invites"

    def setUp(self) -> None:
        amount = 100
        self.user = generateArbitraryUsers(1)[0]
        self.teams = generateArbitraryTeams(amount)
        self.invites = []

        for team_objects in self.teams:
            invite = TeamInvite.objects.create(team=team_objects, user=self.user)
            invite.save()
            self.invites.append(invite)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def testListInvites(self):
        response = self.client.get(reverse(self.prefix + "-list"), format="json")
        serialized_team_list = UserInviteSerializer(self.invites, many=True)

        # this call is not paginated, so what's returned should be equivalent
        # to the serialized_team_list data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized_team_list.data)

    def testAcceptInvite(self):
        for invite in self.invites:
            response = self.client.put(reverse(self.prefix + "-detail", kwargs={"pk": invite.id}),
                        {},
                        format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {"msg": "success"})

        # there should be as many member objects as there are teams, but not
        # invite objects, since we just accepted all of them
        self.assertEqual(Member.objects.filter(owner=self.user).count(), len(self.teams))
        self.assertEqual(TeamInvite.objects.filter(user=self.user).count(), 0)
