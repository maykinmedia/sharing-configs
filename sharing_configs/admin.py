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
    """
    provide methods to collect data in export form and make API call to upload files to storage
    using credentials
    """

    export_template = "sharing_configs/admin/export.html"

    def get_sharing_configs_export_data(self, obj, form):
        """
        provide payload for API by uploading file to storage
        filename: string
        obj(content): file object base64 encoded
        author (optional): string
        """
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id):
        """
        return template with pre-filled form for GET request;
        process form data in POST request and make API call to endpoint in POST request
        """
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.name}.json"}
        if request.method == "POST":
            form = ExportToForm(request.POST, instance=obj, initial=initial)
            if form.is_valid():
                result = form.save(commit=False)
                result.author = request.user
                file_content = self.get_sharing_configs_export_data(obj, form)
                # collect data for request to API point
                filename = form.cleaned_data.get("file_name")
                folder_content = form.cleaned_data.get("folder_content")
                #  api call try/except request.post(...data,...headers)

                msg = format_html(
                    _(
                        "The object {object} has been exported successfully in the {result} result"
                    ),
                    object=obj,
                )
                self.message_user(request, msg, level=messages.SUCCESS)

        else:
            form = ExportToForm(initial=initial, instance=obj)

        return render(
            request,
            self.export_template,
            {"object": obj, "form": form},
        )

    def get_urls(self):
        urls = super().get_urls()

        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path(
                "<path:object_id>/export-to/",
                self.admin_site.admin_view(self.sharing_configs_export_view),
                name="%s_%s_export" % info,
            ),
        ]
        return my_urls + urls


class SharingConfigsImportMixin:
    """provide methods to download files from storage using credentials"""

    import_template = "sharing_configs/admin/import.html"

    def get_sharing_configs_import_data(self, form):
        """
        provide data for API by downloading file from storage
        filename: string
        folder: string
        label: string
        """
        raise NotImplemented

    def import_from_view(self, request):
        """
        return template with form and process data if form filled;
        make API call to API point to download file

        """
        if request.method == "POST":
            form = ImportForm(request.POST)
            if form.is_valid():
                object = form.save()
                msg = format_html(
                    _("The object {object} has been imported successfully!"),
                    object=object,
                )
                self.message_user(request, msg, level=messages.SUCCESS)
                # TODO: adjust path to changelist
                return redirect(reverse("admin:core_objecttype_changelist"))
        else:
            form = ImportForm()

            return render(request, self.import_template, {"form": form})

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-from/",
                self.admin_site.admin_view(self.import_from_view),
                name="import",
            ),
        ]
        return my_urls + urls
