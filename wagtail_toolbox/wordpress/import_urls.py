from django.urls import path

from wagtail_toolbox.wordpress.admin import import_admin_site

urlpatterns = [
    path("", import_admin_site.urls),
]
