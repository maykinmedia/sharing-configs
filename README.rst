
Sharing Configs for Django
=================================================

:Version: 0.1.1
:Source: https://github.com/maykinmedia/sharing-configs
:Keywords: ``django``, ``github``
:PythonVersion: 3.7, 3.8, 3.9

|build-status| |coverage| |black|

|python-versions| |django-versions| |pypi-version|

A reusable Django app to export and import resources using `Sharing Configs API`_.

Developed by `Maykin Media B.V.`_.

Features
========

* provides client to interact with `Sharing Configs API`_
* easy download and upload of resources in the Django admin


Installation
============

Requirements
------------

* Python 3.7 or above
* setuptools 30.3.0 or above
* Django 2.2 or newer


Install
-------

1. Install from PyPI

.. code-block:: bash

    pip install sharing-configs

2. Add ``sharing_configs`` to the ``INSTALLED_APPS`` setting.
3. In the admin page of ``SharingConfigsConfig`` configure access to the Sharing Configs API

Usage
=====

The Sharing Config Library provides two mixins to add into the ModelAdmin class of your resources:
* ``SharingConfigsImportMixin`` - to import the resource
* ``SharingConfigsExportMixin`` - to export the resource

The mixins provide custom admin views and request Sharing Configs API under the hood.

Import
------

To use ``SharingConfigsImportMixin`` the developer should specify how to convert the imported file into the
django model instance and override ``get_sharing_configs_import_data`` method


Export
------

To use ``SharingConfigsExportMixin`` the developer should specify how to convert the django model instance into
the exporting file and override ``get_sharing_configs_export_data`` method


.. |build-status| image:: https://github.com/maykinmedia/sharing-configs/actions/workflows/ci.yaml/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/sharing-configs/actions/workflows/ci.yaml?branch=master

.. |coverage| image:: https://codecov.io/gh/maykinmedia/sharing-configs/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/sharing-configs
    :alt: Coverage status

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/sharing_configs.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/sharing_configs.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/sharing_configs.svg
    :target: https://pypi.org/project/sharing_configs/

.. _Maykin Media B.V.: https://www.maykinmedia.nl
.. _Sharing Configs API: https://github.com/maykinmedia/sharing-configs-api.git

Example
=======
We can use the Sharing Configs library to exchange color-themes for the Django admin with other users. For this, we need a model that stores the color-theme, 
and use the Sharing Configs mixins to import and export the color-theme.

Create two models: Configuration and Theme

.. code-block:: python

    # models.py  
    from django.db import models  
    from solo.models import SingletonModel


    class Configuration(SingletonModel):
        """
        configuration that holds the current theme
        """

        theme = models.ForeignKey("Theme", on_delete=models.CASCADE,null=True)
        


    class Theme(models.Model):
        """All attributes used for theming."""

        name = models.CharField("name", max_length=120)
        primary = models.CharField("primary", max_length=60)
        secondary = models.CharField("secondary", max_length=60)
        accent = models.CharField("accent", max_length=60)
        primary_fg = models.CharField("primary_fg", max_length=60)
        
        
Register the ``Theme`` model in the admin and include our two mixins to introduce the UI to import and export objects, in this case, themes.
Sharing Configs does not know how to import or export your model, so you will need to write this yourself. You 
can override the methods introduced by the mixins: ``get_sharing_configs_export_data`` and ``get_sharing_configs_import_data``

.. code-block:: python
    # admin.py
    import json

    from django.contrib import admin
    from django.forms.models import model_to_dict
    from django.shortcuts import get_object_or_404

    from sharing_configs.admin import SharingConfigsExportMixin, SharingConfigsImportMixin
    from sharing_configs.forms import ExportToForm, ImportForm

    from .models import Configuration, Theme


    class ThemeAdmin(SharingConfigsExportMixin, SharingConfigsImportMixin, admin.ModelAdmin):        

        def get_sharing_configs_export_data(self, obj: object) -> bytes:
            """convert the theme to JSON."""
            theme = get_object_or_404(Theme, id=obj.id)
            theme_dict = model_to_dict(theme)
            theme_dict.pop("id", None)
            dump_json_theme = json.dumps(cleaned_theme_dict, sort_keys=True, default=str)        
            return dump_json_theme.encode("utf-8")

        def get_sharing_configs_import_data(self, content: bytes) -> object:
            """
            Convert JSON to a new theme instance. Typically, the JSON that is read here is the same as that 
            the JSON generated by the above function.
            """              
            decoded_content = content.decode("utf-8")
            theme_dict = json.loads(decoded_content)        
            return ColorTheme.objects.create(**theme_dict)       


That takes care of the import and export functionality for exchaning color-themes. To make it actually working, 
we complete this example with some additional code.
Create a ``context_processors.py`` file, to pass the currently configured theme to the template context:

.. code-block:: python

    def set_admin_color(request:object)->dict:
        """
        create a dictionary of color variables to pass to the base_site.html Django admin page
        """
        conf = Configuration.get_solo()
        theme = conf.theme
        if theme is None:
            return {}

        return {
            "primary": theme.primary,
            "secondary": theme.secondary,            
            "primary_fg": theme.primary_fg,
            "accent": theme.accent
            
        }

Finally, pass the theme context variables to an overriden ``base_site.html`` in the templates folder.

.. code-block::
    
  {% extends "admin/base_site.html" %}
    {% block extrastyle %}
    <html
        style=" --primary:{{primary}}; --secondary:{{secondary}}; --accent:{{accent}}; --primary_fg:{{primary_fg}};">
    </html>
  {% endblock %}

Now you can choose an available color-theme via the configuration inside the Django admin.
