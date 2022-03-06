from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .forms import ExportToGithubForm, GithubImportForm
from .models import GithubConfig


@admin.register(GithubConfig)
class GithubConfigAdmin(SingletonModelAdmin):
    pass


class SharingConfigsExportMixin:
    def get_sharing_configs_export_data(self, obj, **form_kwargs):
        raise NotImplemented

class SharingConfigsExportMixin:
    pass
