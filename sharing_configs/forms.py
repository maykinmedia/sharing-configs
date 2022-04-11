from logging import raiseExceptions

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .fields import FolderChoiceField
from .utils import get_imported_folders_choices


class FolderForm(forms.Form):
    """
    Trigger an API call to get folders available for a given user
    """

    permission = None  # "all"
    folder = forms.ChoiceField(label=_("Folders"), required=True, choices=[])

    def __init__(self, *args, **kwargs):
        """make list of folders available with pre-populated data in drop-down menu based on permissions"""
        params = f"/?permission={self.permission}"
        folder_list = get_imported_folders_choices(params)
        kwargs.setdefault("Choose a folder", list(folder_list))
        super().__init__(*args, **kwargs)


class ImportForm(FolderForm):
    """Provide form  with a list of writable AND readable folders"""

    permission = "all"

    file_name = forms.ChoiceField(
        label=_("File name"),
        required=True,
        help_text=_("Name of the file in storage folder"),
    )

    def clean_file_name(self):
        file_name = self.cleaned_data["file_name"]
        if file_name == "":
            raise forms.ValidationError("File should have a name")
        return file_name


class ExportToForm(FolderForm):
    """Provide form  with a list of writable folders"""

    permission = "write"

    file_name = forms.CharField(
        label=_("File name"),
        max_length=100,
        required=True,
        help_text=_("Name of the file in storage folder"),
    )
    overwrite = forms.BooleanField(
        label=_("Overwrite"),
        required=False,
        initial=False,
        help_text=_("Overwrite the existing file in the storage folder"),
    )

    class Meta:
        fields = ("file_name", "overwrite", "folder_name")
