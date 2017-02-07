"""
URLs for the Microsite API

"""
from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        r'^v1/$',
        views.MicrositeList.as_view(),
        name="microsite_list"
    ),
    url(
        r'^v1/(?P<key>.*)/$',
        views.MicrositeDetail.as_view(),
        name="microsite_detail"
    ),
]
