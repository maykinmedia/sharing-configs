from sharing_configs.admin import SharingConfigsExportMixin

from .utils import export_apps


class SharingConfigsExportAdmin(SharingConfigsExportMixin):
    def get_sharing_configs_export_data(self, obj, **form_kwargs):
        return export_apps()
