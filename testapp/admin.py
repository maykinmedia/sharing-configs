import json

from django.contrib import admin
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from sharing_configs.admin import SharingConfigsExportMixin, SharingConfigsImportMixin
from sharing_configs.forms import ExportToForm, ImportForm
from testapp.models import Configuration, Theme


class ThemeAdmin(SharingConfigsExportMixin, SharingConfigsImportMixin, admin.ModelAdmin):

    sharing_configs_export_form = ExportToForm
    sharing_configs_import_form = ImportForm

    def get_sharing_configs_export_data(self, obj: object) -> bytes:
        """convert Theme model object to a byte like object"""
        theme = get_object_or_404(Theme, id=obj.id)
        theme_dict = model_to_dict(theme)
        theme_dict.pop("id", None)
        dump_json_theme = json.dumps(theme_dict, sort_keys=True, default=str)
        return dump_json_theme.encode("utf-8")

    def get_sharing_configs_import_data(self, content: bytes) -> object:
        """decode byte string and create an object of Theme model
        example of content from API: b'{"accent": "#f8f8f8","name": "spring", "primary": "#8d979c", \
        "primary_fg": "#1a2b3c", "secondary": "#315980"}'
        """
        decoded_content = content.decode("utf-8")
        theme_dict = json.loads(decoded_content)
        return Theme.objects.create(**theme_dict)


admin.site.register(Theme, ThemeAdmin)
admin.site.register(Configuration)
