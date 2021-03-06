import json

from django.contrib import admin
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from solo.admin import SingletonModelAdmin

from sharing_configs.admin import SharingConfigsMixin
from testapp.models import Configuration, Theme


class ThemeAdmin(SharingConfigsMixin, admin.ModelAdmin):
    def get_sharing_configs_export_data(self, obj: object) -> bytes:
        """convert the theme to JSON."""
        theme = get_object_or_404(Theme, id=obj.id)
        theme_dict = model_to_dict(theme)
        theme_dict.pop("id", None)
        dump_json_theme = json.dumps(theme_dict, sort_keys=True, default=str)
        return dump_json_theme.encode("utf-8")

    def get_sharing_configs_import_data(self, content: bytes) -> object:
        """
        Convert JSON to a new theme instance. Typically, the JSON that is read here is the same as that
        the JSON generated by the above function.
        """
        decoded_content = content.decode("utf-8")
        theme_dict = json.loads(decoded_content)
        return Theme.objects.create(**theme_dict)


admin.site.register(Theme, ThemeAdmin)
admin.site.register(Configuration, SingletonModelAdmin)
