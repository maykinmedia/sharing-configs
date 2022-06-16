from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class Configuration(SingletonModel):
    """
    configuration that holds the current theme
    """

    theme = models.ForeignKey("Theme", on_delete=models.SET_NULL, null=True, blank=True)


class Theme(models.Model):
    """All attributes used for theming."""

    name = models.CharField("name", max_length=100)
    primary = models.CharField("primary color", max_length=7)
    secondary = models.CharField("secondary color", max_length=7)
    accent = models.CharField("accent color", max_length=7)
    primary_fg = models.CharField("primary foreground color", max_length=7)

    def __str__(self) -> str:
        return self.name
