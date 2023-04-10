from django.urls import path
from wagtail import hooks

from wagtail_toolbox.checks.views import models_list, models_view


@hooks.register("register_admin_urls")
def register_counter_urls():
    return [
        path("models-list/", models_list, name="models-list"),
        path("models-view/", models_view, name="models-view"),
    ]
