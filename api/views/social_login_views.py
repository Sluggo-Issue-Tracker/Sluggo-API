from allauth.socialaccount.providers.slack.views import SlackOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


class SlackLogin(SocialLoginView):
    adapter_class = SlackOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
