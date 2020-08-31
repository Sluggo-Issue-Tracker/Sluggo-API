from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from ..models import Ticket
from ..models import Profile

import datetime

User = get_user_model()

assigned_dict = dict(email="noah@sicmundus.org", first_name="Hanno", last_name="Tauber")

user_dict = dict(email="adam@sicmundus.org", first_name="Jonas", last_name="Kahnwald")

admin_dict = dict(email="Claudia@wnpp.gov", first_name="Claudia", last_name="Tiedemann")


class ProfileBaseBehavior(TestCase):

    def setUp(self):
        pass

    def testBaseBehavior(self):
        pass

