from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class SharingConfigsConfig(SingletonModel):
    """
    Config for sharing
    """

    api_endpoint = models.URLField(
        _("API endpoint"),
        max_length=250,
        help_text=_("Path to API point. For example: https://www.example.com/api/v1/"),
    )
    api_key = models.CharField(
        _("API key"),
        max_length=128,
        help_text=_("API key for authorization"),
    )
    label = models.CharField(
        _("label"),
        max_length=50,
        help_text=_("This label should match the label in the Sharing Configs API."),
    )
    default_organisation = models.CharField(
        _("default organisation"),
        max_length=100,
        blank=True,
        help_text=_(
            "The default organisation to use in the description when sharing configurations."
        ),
    )

    class Meta:
        verbose_name = _("Sharing Configs configuration")

    def __str__(self):
        return self.label
