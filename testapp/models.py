from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class Configuration(SingletonModel):
    """
    configuration that holds the current theme
    """

    theme = models.ForeignKey("Theme", on_delete=models.CASCADE, null=True)


class Theme(models.Model):
    """All attributes used for theming."""

    name = models.CharField("name", max_length=120)
    primary = models.CharField("primary", max_length=60)
    secondary = models.CharField("secondary", max_length=60)
    accent = models.CharField("accent", max_length=60)
    primary_fg = models.CharField("primary_fg", max_length=60)

    def __str__(self) -> str:
        return self.name
