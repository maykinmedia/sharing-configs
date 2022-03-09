from django.contrib import admin
from django.contrib.auth import get_user_model

from sharing_configs.admin import SharingConfigsExportMixin

from .utils import export_apps

User = get_user_model()


class SharingConfigsExportAdmin(SharingConfigsExportMixin):
    def get_sharing_configs_export_data(self, obj, **form_kwargs):
        return export_apps()


admin.unregister(User)


@admin.register(User)
class UserAdmin(SharingConfigsExportMixin, admin.ModelAdmin):
    pass
