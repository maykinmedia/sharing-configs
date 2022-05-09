from typing import Union

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
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
from .utils import get_imported_files_choices


@admin.register(SharingConfigsConfig)
class SharingConfigsConfig(SingletonModelAdmin):
    pass


User = get_user_model()


class SharingConfigsExportMixin:
    """
    A class that prepares data and privides interface to make API call using credentials;
    The  get_sharing_configs_export_data() method raise NotImplementedError and should be
    overriden in a derived class.
    """

    change_form_template = "sharing_configs/admin/change_form.html"
    change_form_export_template = "sharing_configs/admin/export.html"
    sharing_configs_export_form = ExportToForm

    def get_sharing_configs_export_data(self, obj: object) -> Union[str, bytes]:
        """
        Derived class should provide object to export

        """
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id):
        """
        return template with form for GET request;
        process form data from POST request and make API call to endpoint
        """
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.username}.json"}
        if request.method == "POST":
            form = self.get_sharing_configs_export_form(request.POST, initial=initial)
            if form.is_valid():
                author = request.user.username
                content = self.get_sharing_configs_export_data(obj)
                filename = form.cleaned_data.get("file_name")
                folder = form.cleaned_data.get("folder")
                data = {
                    "overwrite": form.cleaned_data.get("overwrite"),
                    "content": content,
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
                            f"admin:{info[0]}_{info[1]}_export",
                            kwargs={"object_id": obj.id},
                        )
                    )
                except ApiException as e:
                    msg = format_html(
                        _(f"Import of object failed: {e}"),
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
                self.import_template,
                {"form": form, "opts": self.model._meta},
            )

        else:
            form = self.sharing_configs_export_form(initial=initial)

        return render(
            request,
            self.change_form_export_template,
            {"object": obj, "form": form, "opts": obj._meta},
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
    """provide methods to download files(object) from storage using credentials"""

    change_list_template = "sharing_configs/admin/change_list.html"
    import_template = "sharing_configs/admin/import.html"
    sharing_configs_import_form = ImportForm

    def get_sharing_configs_import_data(
        self, filename: str, folder: str, author: str
    ) -> object:
        """
        Derived class should override params to import an object;
        Also need implementation to store a received object

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

    def import_from_view(self, request, **kwargs):
        """
        return template with form and process data if form is bound;
        make API call to API point to download an object

        """
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        if request.method == "POST":
            form = self.get_sharing_configs_import_form(request.POST)
            if form.is_valid():
                folder = form.cleaned_data.get("folder")
                filename = form.cleaned_data.get("file_name")
                obj = SharingConfigsClient()
                try:
                    resp_api_dict = obj.import_data(folder, filename)
                    msg = format_html(
                        _("The (file) object has been imported successfully!"),
                    )
                    self.message_user(request, msg, level=messages.SUCCESS)
                    return redirect(reverse(f"admin:{info[0]}_{info[1]}_import"))

                except ApiException as e:
                    msg = format_html(
                        _(f"Import of object failed: {e}"),
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
                {"form": form, "opts": self.model._meta},
            )
        else:
            form = self.get_sharing_configs_import_form()
            return render(
                request,
                self.import_template,
                {
                    "form": form,
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
