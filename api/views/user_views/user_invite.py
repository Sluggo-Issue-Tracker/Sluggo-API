from api.serializers import *
from api.permissions import IsAuthenticated
from api.models import TeamInvite, Member, Team
from rest_framework import serializers
from rest_framework.response import Response
from django.db import transaction
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin


class UserInviteViewSet(
    GenericViewSet, ListModelMixin, UpdateModelMixin, DestroyModelMixin
):

    permission_classes = [IsAuthenticated]
    serializer_class = UserInviteSerializer
    queryset = TeamInvite.objects.all().prefetch_related("user")
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user)

    def update(self, request, *args, **kwargs) -> Response:
        invite_instance = self.get_object()
        user_instance = invite_instance.user
        team_instance = invite_instance.team

        if Member.objects.filter(owner=user_instance, team=team_instance).exists():
            raise serializers.ValidationError({"team": "this member already exists!"})

        with transaction.atomic():
            Member.objects.create(owner=user_instance, team=team_instance).save()
            invite_instance.delete()

        return Response({"msg": "success"})
