from django.db import models


class TimeStampedModelMixin(models.Model):
    """Model mixin with timestamp fields (created, updated)."""

    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True
