from rest_framework import permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.settings import api_settings

from ..permissions import (
    IsAdminMemberOrReadOnly,
    IsOwnerOrReadOnly,
    IsMemberUser
)

from django.contrib.auth import get_user_model

from ..models import (
    Member,
    Team,
)
from ..serializers import (
    MemberSerializer,
    TeamSerializer,
    UserSerializer
)


class MemberViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """
    Reads handled by the mixins, and use permission_classes
    """

    queryset = Member.objects.all()

    model = Member

    permission_classes = [
        permissions.IsAuthenticated,
        IsMemberUser,
        IsOwnerOrReadOnly
    ]

    serializer_class = MemberSerializer

    @staticmethod
    def get_success_headers(data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    # require only that the user is authenticated to create their profile / join a team
    # manually defining this since we want to offer this endpoint for any authenticated user
    @action(methods=["POST"], detail=False, permission_classes=[permissions.IsAuthenticated])
    def create_record(self, request, *args, **kwargs):
        team_id = request.data.get("team_id")

        try:
            team = Team.objects.get(id=team_id)
            serializer = MemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save(owner=self.request.user, team=team)

            headers = self.get_success_headers(serializer.data)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # this facilitates editing the user profile associated with a team
    # this function is keyed in by the join_id which is the team_id
    # concatenated with the md5 of the user_id
    #
    # affects both the member record and the associated user record
    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        pk = kwargs.pop("pk")

        # serialize the input, then update only a select number of fields
        try:
            member_serializer = MemberSerializer(data=request.data)
            member_serializer.is_valid(raise_exception=True)
            member_data = member_serializer.validated_data

            user_serializer = UserSerializer(data=request.data.get("user"))
            user_serializer.is_valid(raise_exception=True)
            user_data = user_serializer.validated_data

            # only update the fields that the user has access to
            # in their edit profile dialog
            member = Member.objects.get(pk=pk)
            Member.objects.filter(pk=pk).update(
                bio=member_data.get("bio"),
            )

            get_user_model().objects.filter(pk=member.owner.id).update(
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name")
            )

        except Member.DoesNotExist as e:
            return Response({"msg": e.message}, status=status.HTTP_404_NOT_FOUND)

        except exceptions.ValidationError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, partial=True)

    # approve the user if not done already
    # this call is essentially idempotent and only modifies the user record when user was not previously activated
    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsAdminMemberOrReadOnly])
    def approve(self, request, pk=None):
        """ approve the join request """
        self.check_object_permissions(request, self.get_object())

        try:
            member = Member.objects.get(pk=pk)
            member.activated = timezone.now()

            if member.role == Member.Roles.UNAPPROVED:
                member.role = Member.Roles.APPROVED
                member.save(update_fields=["activated", "role"])

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status.HTTP_404_NOT_FOUND)

    # TODO: make the target user an admin

    # make the user an admin if not done already
    # this call is essentially idempotent and only modifies the user record when user was not previously activated
    # the user does not need to be approved for them to become an admin
    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsAdminMemberOrReadOnly])
    def make_admin(self, request, pk=None):
        """ make the user an admin """
        self.check_object_permissions(request, self.get_object())

        try:
            member = Member.objects.get(pk=pk)
            member.activated = timezone.now()

            if member.role != Member.Roles.ADMIN:
                member.save(update_fields=["role"])

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["patch"], permission_classes=permission_classes)
    def leave(self, request, pk=None):
        """ leave this team this is deletion but only to deactivate the record """
        self.check_object_permissions(request, self.get_object())

        try:
            member = Member.objects.get(pk=pk)
            member.deactivated = timezone.now()
            member.save()

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status=status.HTTP_404_NOT_FOUND)


class TeamViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    queryset = Team.objects.all()

    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminMemberOrReadOnly
    ]

    serializer_class = TeamSerializer

    @staticmethod
    def get_success_headers(data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @action(methods=["POST"], detail=False, permission_classes=[permissions.IsAuthenticated])
    def create_record(self, request, *args, **kwargs):
        # serialize the request data.
        team_serializer = TeamSerializer(data=request.data)
        team_serializer.is_valid(raise_exception=True)
        team = team_serializer.save()  # if we've made it this far, save the record

        # construct a member record from the user information
        member = Member.objects.create(
            owner=request.user,
            team=team,
            role="AD",
            activated=timezone.now()
        )
        member.save()

        headers = self.get_success_headers(team_serializer.data)

        return Response(team_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # requiring that all updates are partial instead of full
    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=["GET"])
    def search(self, request, q=None):
        """ retrieve teams based on a user query. this should rank the team queryset by
            1. existence of search terms in the record's title + description
            2. similarity of search terms to words in the record's description + description
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
