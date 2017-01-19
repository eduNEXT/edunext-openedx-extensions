from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthTokenConfig(AppConfig):
    name = 'edunext_openedx_extensions.ednx_microsite_configuration'
    verbose_name = _("Edunext microsite configuration")
