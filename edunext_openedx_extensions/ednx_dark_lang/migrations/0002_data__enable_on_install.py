# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Converted from the original South migration 0002_enable_on_install.py
#
from django.db import migrations, models


def create_ednx_dark_lang_config(apps, schema_editor):
    """
    Enable DarkLang by default when it is installed, to prevent accidental
    release of testing languages.
    """
    EdnxDarkLangConfig = apps.get_model("ednx_dark_lang", "EdnxDarkLangConfig")

    objects = EdnxDarkLangConfig.objects
    if not objects.exists():
        objects.create(enabled=True)


def remove_ednx_dark_lang_config(apps, schema_editor):
    """Write your backwards methods here."""
    raise RuntimeError("Cannot reverse this migration.")


class Migration(migrations.Migration):

    dependencies = [
        ('ednx_dark_lang', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_ednx_dark_lang_config, remove_ednx_dark_lang_config),
    ]
