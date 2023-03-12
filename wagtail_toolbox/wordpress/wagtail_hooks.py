import json

from django.apps import apps
from django.conf import settings
from django.urls import path, reverse
from taggit.models import Tag
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin

from wagtail_toolbox.wordpress.utils import (
    get_django_model_admin_url,
    parse_wordpress_routes,
)
from wagtail_toolbox.wordpress.views import (
    import_wordpress_data_view,
    run_import,
    run_transfer,
    transfer_wordpress_data_view,
)


@hooks.register("construct_settings_menu")
def hide_user_menu_item(request, menu_items):
    """
    Hide the wordpress settings menu item.
    It's moved to the Import Admin menu.
    """

    menu_items[:] = [item for item in menu_items if item.label != "Wordpress settings"]


@hooks.register("register_admin_urls")
def register_import_wordpress_data_url():
    """
    Register the import wordpress data url.

    Returns:
        list: A list of urls.
    """

    return [
        path(
            "import-wordpress-data/",
            import_wordpress_data_view,
            name="import_wordpress_data",
        ),
        path("run_import/", run_import, name="run_import"),
        path(
            "transfer-wordpress-data/",
            transfer_wordpress_data_view,
            name="transfer_wordpress_data",
        ),
        path("run_transfer/", run_transfer, name="run_transfer"),
    ]


@hooks.register("register_admin_menu_item")
def register_import_wordpress_data_menu_item():
    """
    Register the import wordpress data menu items.

    Returns:
        SubmenuMenuItem: The menu item.
    """

    # TODO: find the correct way to resolve the admin urls.
    submenu = Menu(
        items=[
            MenuItem(
                "Settings",
                "/admin/settings/wordpress/wordpresssettings",
                icon_name="cogs",
            ),
            MenuItem(
                "Import Data",
                reverse("import_wordpress_data"),
                icon_name="download-alt",
            ),
            MenuItem(
                "Transfer Data", reverse("transfer_wordpress_data"), icon_name="logout"
            ),
        ]
        + generate_menu_items()  # managed via a django admin site
    )

    return SubmenuMenuItem("WP Import", submenu, icon_name="download", order=1)


def generate_menu_items():
    """
    Generate a list of menu items, one  for each WP model.
    Managed via the django admin.

    Returns:
        list: A list of menu items.
    """

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


@hooks.register("insert_global_admin_js")
def select_config_js():
    # TODO: This is a bit of a hack, but it works for now. It should really only be seen when it needs to be.
    # e.g. when on the wordpress settings page.
    if hasattr(settings, "WPI_HOST"):
        wp_data = {
            "routes": {},
            "models": {},
        }
        wordpress_routes = parse_wordpress_routes(settings.WPI_HOST)
        for route in wordpress_routes:
            for key, value in route.items():
                value["url"] = key
                wp_data["routes"][value["name"]] = value
        for model in apps.get_models():
            if model.__name__.startswith("WP") and hasattr(model, "SOURCE_URL"):
                wp_data["models"][model.get_source_url(model)] = model.__name__

        return f"""
            <script id="wp-select-config" type="application/json">
            { json.dumps(wp_data) }
            </script>
        """


# @hooks.register("insert_global_admin_js")
# def target_models_js():
#     if hasattr(settings, "WPI_ADMIN_TARGET_MODELS"):
#         counts = []
#         for model in settings.WPI_ADMIN_TARGET_MODELS:
#             wagtail_model = apps.get_model(model[0])
#             wordpress_model = apps.get_model(model[1])
#             counts.append(
#                 {
#                     "wagtail_model": wagtail_model.__name__,
#                     "wagtail_count": wagtail_model.objects.count(),
#                     "wordpress_model": wordpress_model.__name__,
#                     "wordpress_count": wordpress_model.objects.count(),
#                 }
#             )
#         return f"""
#             <script id="wp-target-models" type="application/json">
#             { json.dumps(counts) }
#             </script>
#         """


class TagsModelAdmin(ModelAdmin):
    Tag.panels = [FieldPanel("name")]  # only show the name field
    model = Tag
    menu_label = "Tags"
    menu_icon = "tag"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ["name", "slug"]
    search_fields = ("name",)


# modeladmin_register(TagsModelAdmin)
