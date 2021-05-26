from .test_base import *

class MemberTestCase(TeamRelatedCore):
    prefix = "team-members"

    model = Member
    serializer = MemberSerializer

    data_dict = {
        "bio": "biography"
    }

    normal_user_dict = dict(
        username="gov.wnpp.Claudia",
        email="Claudia@wnpp.gov",
        first_name="Claudia",
        last_name="Tiedemann",
    )

    admin_member_dict = {
        "bio": "asdlfkj",
        "role": "AD"
    }

    admin_user_dict = dict(username="lkajsdf", email="asdf@asdfl.c", first_name="lkajsdf", last_name="lmao")

    def setUp(self):
        super().setUp()
        self.normal_user = User.objects.create(**self.normal_user_dict)
        self.client = APIClient()
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=self.data_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.pk = response.data.get("id")

        # force approve the member
        Member.objects.filter(pk=self.pk).update(role=Member.Roles.APPROVED)

    def testCreate(self):
        self.create(self.data_dict)

    def testList(self):
        self.list()

    def testDetail(self):
        self.detail()

    def testUpdate(self):
        updated_dict = self.data_dict
        updated_dict["bio"] = "alsdfkj"

        expected = self.serializer(self.model.objects.get(pk=self.pk)).data
        expected["bio"] = updated_dict["bio"]

        self.update(updated_dict, expected)

    def testDelete(self):
        self.delete()

    def testApprove(self):
        admin_user = User.objects.create(**self.admin_user_dict)
        Member.objects.create(**self.admin_member_dict, owner=admin_user, team=self.team)
        admin_client = APIClient()
        admin_client.force_authenticate(user=admin_user)

        updated_dict = {
            "role": "AD"
        }

        response = admin_client.patch(
            reverse(self.prefix + "-detail", kwargs={TEAM_PK: self.team.id, "pk": self.pk}),
            data=updated_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_dict.get("role"), response.data.get("role"))
        self.assertEqual(response.data, MemberSerializer(Member.objects.get(pk=self.pk)).data)

    def testCreateRoleUntouched(self): # confirm that a new user can only be unapproved
        user = User.objects.create(**self.admin_user_dict)
        client = APIClient()
        client.force_authenticate(user=user)

        weird_data = {
            "bio": "biography",
            "role": "AD"
        }

        response = client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=weird_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("role"), Member.Roles.UNAPPROVED)

