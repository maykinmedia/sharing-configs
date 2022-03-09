from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .forms import ExportToForm, ImportForm
from .models import GithubConfig


@admin.register(GithubConfig)
class GithubConfigAdmin(SingletonModelAdmin):
    pass


class SharingConfigsExportMixin:
    def get_sharing_configs_export_data(self, obj, **form_kwargs):
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.name}.json"}
        if request.method == "POST":
            form = ExportToForm(
                request.POST,
                instance=obj,
                initial=initial,
                export_func=self.get_sharing_configs_export_data,
            )
            if form.is_valid():
                result = form.save()
                msg = format_html(
                    _(
                        "The object {object} has been exported successfully in the {result} result"
                    ),
                    object=obj,
                    result=result.sha,
                )
                self.message_user(request, msg, level=messages.SUCCESS)

        else:
            form = ExportToForm(initial=initial, instance=obj)

        return render(
            request,
            "admin/core/objecttype/export_to.html",
            {"object": obj, "form": form},
        )

    def get_urls(self):
        urls = super().get_urls()

        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path(
                "<path:object_id>/export-to/",
                self.admin_site.admin_view(self.sharing_configs_export_view),
                name="%s_%s_export_to" % info,
            ),
        ]
        return my_urls + urls


class SharingConfigsImportMixin:
    def import_from_view(self, request):
        if request.method == "POST":
            form = ImportForm(request.POST)
            if form.is_valid():
                object = form.save()
                msg = format_html(
                    _("The object {object} has been imported successfully!"),
                    object=object,
                )
                self.message_user(request, msg, level=messages.SUCCESS)
                return redirect(reverse("admin:core_objecttype_changelist"))
        else:
            form = ImportForm()

            return render(
                request, "admin/core/objecttype/import_from.html", {"form": form}
            )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-from/",
                self.admin_site.admin_view(self.import_from_view),
                name="import_from",
            ),
        ]
        return my_urls + urls
