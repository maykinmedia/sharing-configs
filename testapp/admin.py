from django.contrib import admin
from django.contrib.auth import get_user_model

from sharing_configs.admin import SharingConfigsExportMixin, SharingConfigsImportMixin
from sharing_configs.forms import ExportToForm, ImportForm

from .utils import export_apps

User = get_user_model()

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(SharingConfigsExportMixin, SharingConfigsImportMixin, admin.ModelAdmin):

    sharing_configs_export_form = ExportToForm
    sharing_configs_import_form = ImportForm

    def get_sharing_configs_export_data(self, obj: object) -> str:
        """current state: return list"""
        return export_apps()
