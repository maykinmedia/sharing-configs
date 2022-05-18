from django.contrib import admin
from django.contrib.auth import get_user_model
import json
from sharing_configs.admin import SharingConfigsExportMixin, SharingConfigsImportMixin
from sharing_configs.forms import ExportToForm, ImportForm
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from .utils import export_apps

User = get_user_model()

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(SharingConfigsExportMixin, SharingConfigsImportMixin, admin.ModelAdmin):

    sharing_configs_export_form = ExportToForm
    sharing_configs_import_form = ImportForm

    def get_sharing_configs_export_data(self, obj: object) -> bytes:
        """return  django user model object as a byte like object"""

        user = get_object_or_404(User, id=obj.id)
        user_dict = model_to_dict(user)
        dump_json_user = json.dumps(user_dict, sort_keys=True, default=str)
        return dump_json_user.encode("utf-8")

    # def get_sharing_configs_export_data(self, obj: object) -> str:
    #     """current state: return list"""
    #     return export_apps()

    def get_sharing_configs_import_data(self, content: bytes) -> object:
        """current state: return list"""
        print(content)
