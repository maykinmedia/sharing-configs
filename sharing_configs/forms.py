from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .fields import FolderChoiceField


class ImportForm(forms.Form):
    """
    custom FolderChoiceField creation triggers an API call to (per)populate drop-down menu
    for folders available for a given user
    """

    folder = FolderChoiceField(label=_("Folders"), required=True)
    file_name = forms.ChoiceField(
        label=_("File name"),
        required=False,
        help_text=_("Name of the file in storage folder"),
    )


class ExportToForm(forms.Form):

    file_name = forms.CharField(
        label=_("File name"),
        max_length=100,
        required=True,
        help_text=_("Name ot the file in storage folder"),
    )
    overwrite = forms.BooleanField(
        label=_("Overwrite"),
        required=False,
        initial=False,
        help_text=_("Overwrite the existing file in the storage folder"),
    )
    folder_name = forms.CharField(
        label=_("Folder"),
        required=False,
    )

    class Meta:
        fields = ("file_name", "overwrite", "folder_name")
