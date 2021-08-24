from .team_related_base import *
from api.serializers import *
from api.permissions import *
from api.docs import *


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().prefetch_related("member")
    serializer_class = TeamSerializer
    permission_classes = [IsAdminMemberOrReadOnly, IsMemberUser, IsAuthenticated]

    search_fields = ["^name"]
    ordering_fields = ["created", "activated"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(member__owner=request.user)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # create a member record for the requesting user
        Member.objects.create(
            team=instance, owner=request.user, role=Member.Roles.ADMIN
        ).save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
