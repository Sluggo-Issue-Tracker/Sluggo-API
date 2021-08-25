from django.urls import include, path
from django.contrib import admin
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .team_urls import buildTeamRouterUrls
from .user_urls import buildUserRouterUrls
from api import views

urlpatterns = [
    # Optional UI:
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/", include(buildTeamRouterUrls())),
    path("api/user/", include(buildUserRouterUrls())),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("auth/slack/", views.SlackLogin.as_view(), name="slack_login"),
    path("auth/accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
]
