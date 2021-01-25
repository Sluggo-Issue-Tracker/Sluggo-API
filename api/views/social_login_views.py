from allauth.socialaccount.providers.slack.views import SlackOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

"""
The following views are used for slack integration
"""


# this defines the slack login views
class SlackLogin(SocialLoginView):
    adapter_class = SlackOAuth2Adapter
