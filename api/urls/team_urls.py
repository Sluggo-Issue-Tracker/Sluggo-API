from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter, SimpleRouter
from api import views


def buildTeamRouterUrls() -> list:
    team_router = SimpleRouter()
    team_router.register("teams", views.TeamViewSet)

    team_related_router = routers.NestedSimpleRouter(team_router, r"teams", lookup="team")

    team_related_router.register(r"tickets", views.TicketViewSet, basename="team-tickets")

    team_related_router.register(r"members", views.MemberViewSet, basename="team-members")

    team_related_router.register(r"statuses", views.StatusViewSet, basename="team-statuses")

    team_related_router.register(r"tags", views.TagViewSet, basename="team-tags")

    team_related_router.register(r"events", views.EventViewSet, basename="team-events")

    team_related_router.register(r"invites", views.TeamInviteViewSet, basename="team-invites")

    members_router = routers.NestedSimpleRouter(team_related_router, r"members", lookup="member")
    members_router.register(
        r"pinned_tickets", views.PinnedTicketViewSet, basename="pinned-tickets"
    )

    return [
        *team_router.urls,
        *team_related_router.urls,
        *members_router.urls
    ]





