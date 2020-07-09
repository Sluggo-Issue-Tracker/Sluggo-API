from rest_framework import permissions, viewsets
from django.contrib.auth.models import User

from .models import Profile
from .serializers import ProfileSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


#  REST Tutorial Below #

from .models import Snippet
from .serializers import SnippetSerializer
from rest_framework.decorators import action
from rest_framework import renderers
from rest_framework.response import Response


class SnippetViewSet(viewsets.ModelViewSet):
    """
    Lists all code snippets, or creates a new snippet
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)
