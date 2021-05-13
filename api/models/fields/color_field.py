from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re


class ColorField(models.CharField):
    default_validators = []

    def __init__(self, *args, **kwargs):
        colorRE = re.compile('#([A-Fa-f0-9]{8})$')
        self.default_validators.append(RegexValidator(
            colorRE, _('Enter a valid hexA color, eg. #00000000'), 'invalid'))

        kwargs.setdefault('max_length', 9)
        super().__init__(*args, **kwargs)
