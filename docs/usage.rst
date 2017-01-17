=====
Usage
=====

To use edunext-openedx-extensions in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'edunext_openedx_extensions.apps.EdunextOpenedxExtensionsConfig',
        ...
    )

Add edunext-openedx-extensions's URL patterns:

.. code-block:: python

    from edunext_openedx_extensions import urls as edunext_openedx_extensions_urls


    urlpatterns = [
        ...
        url(r'^', include(edunext_openedx_extensions_urls)),
        ...
    ]
