import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from .exceptions import ApiException
from .utils import get_imported_folders_choices

logger = logging.getLogger(__name__)


class FolderForm(forms.Form):
    """
    Trigger an API call to get folders available for a given user
    """

    permission = None

    folder = forms.ChoiceField(label=_("Folders"), required=True, choices=[])

    def __init__(self, *args, **kwargs):
        """provide a list of folders(from API) for a drop-down menu based on permission.
        if api call fails raise custom exception"""
        super().__init__(*args, **kwargs)

        folder_list = [(None, _("Choose a folder"))]
        try:
            folder_list.extend(get_imported_folders_choices(self.permission))
        except ApiException as err:
            logger.exception("Could not retrieve folders: %s" % err)

        self.fields["folder"].choices = folder_list


class ImportForm(FolderForm):
    """Provide form  with a list of readable folders"""

    file_name = forms.CharField(
        label=_("File name"),
        widget=forms.Select,
        required=True,
        help_text=_("Select one of the available files from the community."),
    )

    def clean_file_name(self):
        file_name = self.cleaned_data["file_name"]
        if file_name == "":
            raise forms.ValidationError(_("You must select a file to import."))
        return file_name


class ExportToForm(FolderForm):
    """Provide form with a list of writable folders"""

    permission = "write"

    file_name = forms.CharField(
        label=_("File name"),
        required=True,
        help_text=_("Name of the file to export to the community."),
    )

    overwrite = forms.BooleanField(
        label=_("Overwrite"),
        required=False,
        initial=False,
        help_text=_("Overwrite an existing file if present."),
    )
