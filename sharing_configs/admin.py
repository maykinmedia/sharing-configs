from django.contrib import admin, messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from sharing_configs.client_util import SharingConfigsClient
from sharing_configs.exceptions import ApiException
from sharing_configs.models import SharingConfigsConfig

from .exceptions import ApiException
from .forms import ExportToForm, ImportForm
from .utils import get_imported_files_choices, get_str_from_encoded64_object


@admin.register(SharingConfigsConfig)
class SharingConfigsConfig(SingletonModelAdmin):
    pass


class SharingConfigsExportMixin:
    """
    A class that prepares data and privides interface to make API call using credentials;
    The  get_sharing_configs_export_data() method raise NotImplementedError and should be
    overriden in a derived class.
    """

    change_form_template = "sharing_configs/admin/change_form.html"
    change_form_export_template = "sharing_configs/admin/export.html"
    sharing_configs_export_form = ExportToForm

    def get_sharing_configs_export_data(self, obj: object) -> bytes:
        """
        The developer should override this method for export converting model object into bytes
        that will be futher base64 encoded before sent to the API

        """
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id, extra_context=None):
        """
        return template with form for GET request;
        process form data from POST request and make API call to endpoint;
        initial expects str representation of an object
        """
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        main_url = f"admin:{info[0]}_{info[1]}_export"
        extra_context = extra_context or {}
        extra_context["main_url"] = main_url
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj}.json"}
        if request.method == "POST":

            form = self.get_sharing_configs_export_form(request.POST, initial=initial)
            if form.is_valid():

                author = request.user.username
                byte_content = self.get_sharing_configs_export_data(obj)
                str_content_64_encoded = get_str_from_encoded64_object(byte_content)
                filename = form.cleaned_data.get("file_name")
                folder = form.cleaned_data.get("folder")
                data = {
                    "overwrite": form.cleaned_data.get("overwrite"),
                    "content": str_content_64_encoded,
                    "author": author,
                    "filename": filename,
                }

                obj_client = SharingConfigsClient()
                try:
                    resp = obj_client.export(folder, data)
                    msg = format_html(
                        _("The object {object} has been exported successfully"),
                        object=obj,
                    )
                    self.message_user(request, msg, level=messages.SUCCESS)
                    return redirect(
                        reverse(
                            main_url,
                            kwargs={"object_id": obj.id},
                        )
                    )
                except ApiException:
                    msg = format_html(
                        _("Export of object failed"),
                    )
                    self.message_user(request, msg, level=messages.ERROR)

            if not form.is_valid():
                msg = format_html(
                    _("The object {object} has been not exported"),
                    object=obj,
                )
                self.message_user(request, msg, level=messages.ERROR)

            return render(
                request,
                self.change_form_export_template,
                {
                    "form": form,
                    "extra_context": extra_context,
                    "opts": self.model._meta,
                },
            )
        else:
            form = self.sharing_configs_export_form(initial=initial)

            return render(
                request,
                self.change_form_export_template,
                {
                    "object": obj,
                    "form": form,
                    "extra_context": extra_context,
                    "opts": obj._meta,
                },
            )

    def get_urls(self):
        urls = super().get_urls()
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        add_urls = [
            path(
                "<path:object_id>/export/",
                self.admin_site.admin_view(self.sharing_configs_export_view),
                name=f"{info[0]}_{info[1]}_export",
            ),
        ]

        return add_urls + urls

    def get_sharing_configs_export_form(self, *args, **kwargs):
        """return object export form"""
        if self.sharing_configs_export_form is not None:
            form = self.sharing_configs_export_form(*args, **kwargs)
            return form


class SharingConfigsImportMixin:
    """provide methods to download files from the storage using credentials"""

    change_list_template = "sharing_configs/admin/change_list.html"
    import_template = "sharing_configs/admin/import.html"
    sharing_configs_import_form = ImportForm

    def get_sharing_configs_import_data(self, content: bytes) -> object:
        """
        The developer should override this method decoding bytes and
        creating or updating an model object from the content data.
        """
        raise NotImplemented

    def get_ajax_fetch_files(self, request, *args, **kwargs):
        """ajax call to pass chosen folder to a view"""
        folder = request.GET.get("folder_name")
        api_response_list_files = get_imported_files_choices(folder)
        if api_response_list_files:
            return JsonResponse({"resp": api_response_list_files, "status_code": 200})
        else:
            return JsonResponse({"status_code": 400, "error": "Unable to get folders"})

    def import_from_view(self, request, extra_context=None):
        """
        return template with form and process data if form is bound;
        make API call to API point to download an object

        """
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        main_url = f"admin:{info[0]}_{info[1]}_import"
        ajax_url = f"admin:{info[0]}_{info[1]}_ajax"
        extra_context = extra_context or {}
        extra_context["main_url"] = main_url
        extra_context["ajax_url"] = ajax_url
        if request.method == "POST":

            form = self.get_sharing_configs_import_form(request.POST)
            if form.is_valid():
                folder = form.cleaned_data.get("folder")
                filename = form.cleaned_data.get("file_name")

                obj_client = SharingConfigsClient()
                try:

                    content = obj_client.import_data(folder, filename)
                    obj = self.get_sharing_configs_import_data(content)
                    msg = format_html(
                        _("The (file) object {object} has been imported successfully!"),
                        object=obj,
                    )
                    self.message_user(request, msg, level=messages.SUCCESS)
                    return redirect(reverse(main_url))

                except ApiException:

                    msg = format_html(
                        _("Import of object failed"),
                    )
                    self.message_user(request, msg, level=messages.ERROR)

            if not form.is_valid():

                msg = format_html(
                    _("Something went wrong during object import"),
                )

                self.message_user(request, msg, level=messages.ERROR)

            return render(
                request,
                self.import_template,
                {
                    "form": form,
                    "extra_context": extra_context,
                    "opts": self.model._meta,
                },
            )

        else:
            form = self.get_sharing_configs_import_form()
            return render(
                request,
                self.import_template,
                {
                    "form": form,
                    "extra_context": extra_context,
                    "opts": self.model._meta,
                },
            )

    def get_urls(self):
        urls = super().get_urls()
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )

        add_urls = [
            path(
                "fetch/files/",
                self.admin_site.admin_view(self.get_ajax_fetch_files),
                name=f"{info[0]}_{info[1]}_ajax",
            ),
            path(
                "import/",
                self.admin_site.admin_view(self.import_from_view),
                name=f"{info[0]}_{info[1]}_import",
            ),
        ]

        return add_urls + urls

    def get_sharing_configs_import_form(self, *args, **kwargs):
        """return object of import form"""
        if self.sharing_configs_import_form is not None:
            form = self.sharing_configs_import_form(*args, **kwargs)
            return form
