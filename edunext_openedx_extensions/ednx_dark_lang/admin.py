"""
Admin site bindings for dark_lang
"""

from django.contrib import admin

from config_models.admin import ConfigurationModelAdmin  # pylint: disable=import-error
from edunext_openedx_extensions.ednx_dark_lang.models import EdnxDarkLangConfig

admin.site.register(EdnxDarkLangConfig, ConfigurationModelAdmin)
