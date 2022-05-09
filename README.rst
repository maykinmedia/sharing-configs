
Sharing Configs for Django
=================================================

:Version: 0.1.0
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