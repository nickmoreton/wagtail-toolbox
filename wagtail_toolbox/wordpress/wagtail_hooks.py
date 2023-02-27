import json

from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from wagtail_toolbox.wordpress.models import WPCategory
from wagtail_toolbox.wordpress.panels import wordpress_routes
from wagtail_toolbox.wordpress.views import import_wordpress_data_view


class WPCategoryAdmin(ModelAdmin):
    model = WPCategory
    list_display = ("name", "slug", "parent")
    search_fields = ("name",)
    add_to_admin_menu = False


wp_category_url_helper = WPCategoryAdmin().url_helper

modeladmin_register(WPCategoryAdmin)


@hooks.register("register_admin_urls")
def register_import_wordpress_data_url():
    return [
        path(
            "import-wordpress-data/",
            import_wordpress_data_view,
            name="import_wordpress_data",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_import_wordpress_data_menu_item():
    submenu = Menu(
        items=[
            MenuItem(
                "WP Categories", wp_category_url_helper.index_url, icon_name="table"
            ),
            MenuItem(
                "Import Data", reverse("import_wordpress_data"), icon_name="download"
            ),
        ]
    )

    return SubmenuMenuItem("WP Importer", submenu, icon_name="download-alt")


@hooks.register("insert_global_admin_js")
def global_admin_js():
    wp_data = {}
    for route in wordpress_routes():
        for key, value in route.items():
            value["url"] = key
            wp_data[value["name"]] = value
    return f"""
        <script id="wp-select-config" type="application/json">
        { json.dumps(wp_data) }
        </script>
    """
