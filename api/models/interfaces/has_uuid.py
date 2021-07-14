from django.db import models
import uuid


class HasUuid(models.Model):
    object_uuid = models.UUIDField(
        null=True, blank=False, default=uuid.uuid4, editable=False, unique=True
    )

    class Meta:
        app_label = "api"
        abstract = True

    def __str__(self):
        return f"HasUuid: {self.id}"
