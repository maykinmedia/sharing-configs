import json
import os
from typing import Tuple, Union

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from sharing_configs.models import SharingConfigsConfig

from .forms import ExportToForm, ImportForm
from .utils import get_files_in_folder_from_api, get_imported_files_choices


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
        current state: export a string(or object.attr that has a string representaion)
        # future: API expects an object == File(bytes)
        """
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id):
        """
        return template with form for GET request;
        process form data from POST request and make API call to endpoint
        """
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.username}.json"}
        if request.method == "POST":
            form = self.get_sharing_configs_export_form(request.POST, initial=initial)
            if form.is_valid():
                author = request.user
                obj_to_export = self.get_sharing_configs_export_data(obj)
                file_name = form.cleaned_data.get("file_name")
                folder_name = form.cleaned_data.get("folder_name")
                # get_files_in_folder_from_api
                #  api call try/except request.post(url,data,headers)
                msg = format_html(
                    _("The object {object} has been exported successfully"),
                    object=obj,
                )
                self.message_user(request, msg, level=messages.SUCCESS)

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
        my_urls = [
            path(
                "<path:object_id>/export/",
                self.admin_site.admin_view(self.sharing_configs_export_view),
                name=f"{info[0]}_{info[1]}_export",
            ),
        ]

        return my_urls + urls

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
        folder = request.GET.get("folder_name")
        # API call to fetch files for a given folder
        api_response_list_files = get_imported_files_choices(folder)
        if api_response_list_files:
            return JsonResponse({"resp": api_response_list_files, "status_code": 200})
        else:
            return JsonResponse({"status_code": 400, "error": "Unable to get folders"})

    def import_from_view(self, request, **kwargs):
        """
        return template with form and process data if form is filled;
        make API call to API point to download an object

        """
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        if request.method == "POST":
            form = self.get_sharing_configs_import_form(request.POST)
            file_name = form.data.get("file_name")
            form.fields["file_name"].choices = [(file_name, file_name)]
            if form.is_valid():
                data = {
                    "folder": form.cleaned_data.get("folder"),
                    "filename": form.cleaned_data.get("file_name"),
                }
                # TODO: call to API to fetch object using form data
                # data to be send to API (needs label from settings)
                # resp = requests.post()

                msg = format_html(
                    _("The object {object} has been imported successfully!"),
                    object=object,
                )
                self.message_user(request, msg, level=messages.SUCCESS)
                return redirect(reverse(f"admin:{info[0]}_{info[1]}_import"))

            else:
                # form is NOT valid
                return render(
                    request,
                    self.import_template,
                    {"form": form, "opts": self.model._meta, "perm": "export"},
                )
        else:
            # field folder is pre-filled with resp from API (does not exist yet)
            # current source == json file with data
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

        my_urls = [
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

        return my_urls + urls

    def get_sharing_configs_import_form(self, *args, **kwargs):
        """return object import form"""
        if self.sharing_configs_import_form is not None:
            form = self.sharing_configs_import_form(*args, **kwargs)
            return form
