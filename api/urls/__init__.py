from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .team_urls import buildTeamRouterUrls
from .user_urls import buildUserRouterUrls
from api import views
from api.settings import BASE_URL
from ..admin import sluggo_admin

urlpatterns = [
    # Optional UI:
    path(BASE_URL + "api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        BASE_URL + "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        BASE_URL + "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(BASE_URL + "api/", include(buildTeamRouterUrls())),
    path(BASE_URL + "api/user/", include(buildUserRouterUrls())),
    path(BASE_URL + "auth/", include("dj_rest_auth.urls")),
    path(BASE_URL + "auth/registration/", include("dj_rest_auth.registration.urls")),
    path(BASE_URL + "auth/slack/", views.SlackLogin.as_view(), name="slack_login"),
    path(BASE_URL + "auth/accounts/", include("allauth.urls")),
    path(BASE_URL + "admin/", sluggo_admin.urls),
]
