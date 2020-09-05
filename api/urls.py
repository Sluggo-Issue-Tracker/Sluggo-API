"""
This project will house Andrew's testing of REST API things
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views as api_views

router = DefaultRouter()

# social stuff
router.register(r"member", api_views.MemberViewSet)
router.register(r"team", api_views.TeamViewSet)

# ticket stuff
router.register(r"ticket", api_views.TicketViewSet)
router.register(r"ticket-comment", api_views.TicketCommentViewSet)
router.register(r"ticket-status", api_views.TicketStatusViewSet)

print(router.urls)

urlpatterns = [path("", include(router.urls))]

urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]
