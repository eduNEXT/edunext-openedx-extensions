"""
edraak_i18n app url
"""

from django.conf.urls import patterns, url

from edunext_openedx_extensions.edraak_i18n.views import set_language


urlpatterns = patterns(
    '',
    url(r'^changelang/$', set_language, name='edraak_setlang'),
)
