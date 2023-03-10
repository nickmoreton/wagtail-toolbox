from django.urls import re_path

from wagtail_toolbox.wordpress.views import ApiView

urlpatterns = [
    re_path("", ApiView.as_view(), name="view"),
]
