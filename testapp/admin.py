from django.contrib import admin
from django.contrib.auth import get_user_model

from sharing_configs.admin import SharingConfigsExportMixin

from .utils import export_apps

User = get_user_model()

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(SharingConfigsExportMixin, admin.ModelAdmin):
    def get_sharing_configs_export_data(self, obj: object) -> str:
        return export_apps()
        # current state: return -> list
