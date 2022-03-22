from django import forms

from .utils import get_imported_folders_choices


class FolderChoiceField(forms.ChoiceField):
    """create list of available folders via api call"""

    def __init__(self, *args, **kwargs):
        """make list of folders available with pre-poplated data in drop-down menu"""
        lst = get_imported_folders_choices()
        lst.insert(0, (None, "Choose a folder"))
        kwargs["choices"] = lst
        super().__init__(*args, **kwargs)
