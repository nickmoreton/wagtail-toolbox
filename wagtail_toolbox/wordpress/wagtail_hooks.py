from django.apps import apps
from django.urls import path, reverse
from taggit.models import Tag
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin

from wagtail_toolbox.wordpress.utils import get_django_model_admin_url
from wagtail_toolbox.wordpress.views import (
    import_wordpress_data_view,
    run_import,
    run_transfer,
    transfer_wordpress_data_view,
)


@hooks.register("construct_settings_menu")
def hide_user_menu_item(request, menu_items):
    # so the wordpress are not shown in the settings menu
    menu_items[:] = [item for item in menu_items if item.label != "Wordpress host"]


@hooks.register("register_admin_urls")
def register_import_wordpress_data_url():
    return [
        path(
            "import-wordpress-data/",
            import_wordpress_data_view,
            name="import_wordpress_data",
        ),
        path("run-import/", run_import, name="run-import"),
        path(
            "transfer-wordpress-data/",
            transfer_wordpress_data_view,
            name="transfer-wordpress-data",
        ),
        path("run-transfer/", run_transfer, name="run-transfer"),
    ]


@hooks.register("register_admin_menu_item")
def register_import_wordpress_data_menu_item():
    # TODO: find the correct way to resolve the admin urls.
    submenu = Menu(
        items=[
            MenuItem(
                "Wordpress Host",
                "/admin/settings/wordpress/wordpresshost",
                icon_name="cogs",
            ),
            MenuItem(
                "Import Data",
                reverse("import_wordpress_data"),
                icon_name="download-alt",
            ),
            MenuItem(
                "Transfer Data", reverse("transfer-wordpress-data"), icon_name="logout"
            ),
        ]
        + generate_menu_items()  # managed via a django admin site
    )

    return SubmenuMenuItem("WP Import", submenu, icon_name="download", order=1)


def generate_menu_items():
    # Items managed via the django admin.
    wp_models = [
        model for model in apps.get_models() if model.__name__.startswith("WP")
    ]
    menu_items = []
    for model in wp_models:
        menu_items.append(
            MenuItem(
                f"WP {model._meta.verbose_name_plural}",
                get_django_model_admin_url(model.__name__.lower()),
                icon_name="table",
            )
        )

    return menu_items


class TagsModelAdmin(ModelAdmin):
    # To limit which fields are editable in the admin, use:
    # Tag.panels = [FieldPanel("name")]
    model = Tag
    menu_label = "Tags"
    menu_icon = "tag"
    menu_order = 200
    list_display = ["name", "slug"]
    search_fields = ("name",)
