from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import exceptions

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


class MemberViewSet(viewsets.ModelViewSet):
    """
    CRUD stuff inherited from ModelViewSet
    """

    queryset = Member.objects.all()

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = MemberSerializer

    # i think it should be reasonable that when members are created, the authenticated user
    # is the one that the member record references
    def create(self, request, *args, **kwargs):
        team_id = request.data.get("team_id")

        try:
            team = Team.objects.get(id=team_id)
            serializer = MemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save(user=self.request.user, team=team)

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

            get_user_model().objects.filter(pk=member.user.id).update(
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name")
            )

        except Member.DoesNotExist as e:
            return Response({"msg": e.message}, status=status.HTTP_404_NOT_FOUND)

        except exceptions.ValidationError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, partial=True)

    @action(detail=True, methods=["patch"])
    def approve(self, request, pk=None):
        """ approve the join request """
        try:
            member = Member.objects.get(pk=pk)
            member.activated = timezone.now()
            member.save(update_fields=["activated"])

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["patch"])
    def leave(self, request, pk=None):
        """ leave this team this is deletion but only to deactivate the record """

        try:
            member = Member.objects.get(pk=pk)
            member.deactivated = timezone.now()
            member.save()

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status=status.HTTP_404_NOT_FOUND)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = TeamSerializer

    # requiring that all updates are partial instead of full
    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def search(self, request, q=None):
        """ retrieve teams based on a user query. this should rank the team queryset by
            1. existence of search terms in the record's title + description
            2. similarity of search terms to words in the record's description + description
        """
        queryset = self.filter_queryset(self.get_queryset())

        print(q)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
