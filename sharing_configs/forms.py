import json

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .fields import GitHubFileField
from .github import create_file, get_files_in_folder, get_user, update_file
from .utils import download_file


class GithubImportForm(forms.Form):
    file_path = GitHubFileField(
        label=_("File"),
        widget=forms.RadioSelect,
    )

    def clean_file_path(self):
        url = self.cleaned_data["file_path"]
        self.cleaned_data["file"] = download_file(url)

    @transaction.atomic()
    def save(self):
        # FIXME refactor
        form_file = self.cleaned_data.get("file")

        return super().save()


class ExportToGithubForm(forms.ModelForm):
    file_name = forms.CharField(
        label=_("File name"),
        max_length=100,
        required=True,
        help_text=_("Name ot the file in Github folder"),
    )
    overwrite = forms.BooleanField(
        label=_("Overwrite"),
        required=False,
        initial=False,
        help_text=_("Overwrite the existing file in the GitHub folder"),
    )
    github_folder_content = GitHubFileField(
        label=_("Folder content"),
        widget=forms.RadioSelect,
        disabled=True,
        required=False,
    )
    github_user = forms.CharField(
        label=_("User"),
        disabled=True,
        required=False,
        help_text=_("Github user. Can be configured in the Github Config page"),
    )

    class Meta:
        fields = ("file_name", "overwrite", "github_folder_content", "github_user")

    def save(self, *args, **kwargs):
        # fixme refactor
        json_schema = self.instance.last_version.json_schema
        json_str = json.dumps(json_schema)
        file_name = self.cleaned_data["file_name"]
        update = self.cleaned_data["update"]

        if update:
            return update_file(file_name, json_str)

        return create_file(file_name, json_str)

    def get_initial_for_field(self, field, field_name):
        if field_name == "github_user":
            user = get_user()
            return user.name

        return super().get_initial_for_field(field, field_name)

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

    def __init__(self, *args, **kwargs):
        self.export_func = kwargs.pop("export_func")
        super().__init__(*args, **kwargs)
