import json

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .fields import FileField
from .github import create_file, get_files_in_folder, get_user, update_file
from .utils import download_file


class ImportForm(forms.Form):
    file_name = forms.CharField(
        label=_("File name"),
        max_length=100,
        required=True,
        help_text=_("Name of the file in storage folder"),
    )

    folder = FileField(
        label=_("Folder content"),
        disabled=True,  # ?
        required=False,
    )

    def clean_file_name(self):
        url = self.cleaned_data["file_name"]
        self.cleaned_data["file"] = download_file(url)

    @transaction.atomic()
    def save(self):
        # FIXME refactor
        form_file = self.cleaned_data.get("file_name")
        # form_file = self.cleaned_data.get("file")
        return super().save()


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
    folder_content = forms.CharField(
        label=_("Folder"),
        disabled=True,  # ?
        required=False,
    )
    user = forms.CharField(
        label=_("User"),
        required=False,
        help_text=_("User"),
    )

    class Meta:
        fields = ("file_name", "overwrite", "folder_content", "user")

    def clean_file_name(self):
        file_name = self.cleaned_data["file_name"]
        overwrite = bool(self.data.get("overwrite", "").lower() == "on")

        self.cleaned_data["update"] = False
        existing_file_names = [file.name for file in get_files_in_folder()]

        if file_name in existing_file_names:
            self.cleaned_data["update"] = True

            if not overwrite:
                raise ValidationError(
                    "File with this name already exists. "
                    "Check 'overwrite' if you want to update the existing file "
                )
        return file_name
