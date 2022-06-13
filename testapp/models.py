from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class Configuration(SingletonModel):
    """
    configuration for export/import admin color theme
    """

    theme = models.ForeignKey("Theme", on_delete=models.CASCADE, related_name="theme")

    def __str__(self) -> str:
        return self.theme.name


class Theme(models.Model):
    """object to change color theme in admin"""

    name = models.CharField(_("theme_name"), max_length=120)
    primary = models.CharField(_("primary color"), max_length=60)
    secondary = models.CharField(_("secondary color"), max_length=60)
    accent = models.CharField(_("accent color"), max_length=60)
    primary_fg = models.CharField(_("primary_fg"), max_length=60)

    def __str__(self) -> str:
        return self.name
