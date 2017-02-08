"""
Django admin page for microsite model
"""
from django.contrib import admin

from .models import Microsite


class MicrositeAdmin(admin.ModelAdmin):
    list_display = [
        'key',
        'subdomain',
        'sitename',
        'template_dir',
        'course_org_filter',
    ]
    readonly_fields = (
        'sitename',
        'template_dir',
        'course_org_filter',
    )
    search_fields = ('key', 'subdomain', 'values', )

    def sitename(self, microsite):
        try:
            return microsite.values.get('SITE_NAME', "NOT CONFIGURED")
        except Exception, e:
            return unicode(e)

    def template_dir(self, microsite):
        try:
            return microsite.values.get('template_dir', "NOT CONFIGURED")
        except Exception, e:
            return unicode(e)

    def course_org_filter(self, microsite):
        try:
            return microsite.values.get('course_org_filter', "NOT CONFIGURED")
        except Exception, e:
            return unicode(e)


admin.site.register(Microsite, MicrositeAdmin)
