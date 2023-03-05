import json

from django.apps import apps
from django.conf import settings
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem

from wagtail_toolbox.wordpress.utils import (
    get_django_model_admin_url,
    parse_wordpress_routes,
)
from wagtail_toolbox.wordpress.views import import_wordpress_data_view, run_import


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
    ]


@hooks.register("register_admin_menu_item")
def register_import_wordpress_data_menu_item():
    """
    Register the import wordpress data menu items.

    Returns:
        SubmenuMenuItem: The menu item.
    """

    submenu = Menu(
        items=[
            MenuItem(
                "Import Data", reverse("import_wordpress_data"), icon_name="download"
            ),
        ]
        + generate_menu_items()  # managed via a django admin site
    )

    return SubmenuMenuItem("Import Admin", submenu, icon_name="download-alt", order=1)


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
def global_admin_js():
    # TODO: This is a bit of a hack, but it works for now. It should really only be seen when it needs to be.
    # e.g. when on the wordpress settings page.
    if hasattr(settings, "WP_IMPORTER_HOST"):
        wp_data = {
            "routes": {},
            "models": {},
        }
        wordpress_routes = parse_wordpress_routes(settings.WP_IMPORTER_HOST)
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
