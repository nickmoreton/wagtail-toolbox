import json

from django.apps import apps
from django.conf import settings
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from wagtail_toolbox.wordpress.models import WPAuthor, WPCategory, WPPost, WPTag
from wagtail_toolbox.wordpress.utils import parse_wordpress_routes
from wagtail_toolbox.wordpress.views import import_wordpress_data_view, run_import


class WPCategoryAdmin(ModelAdmin):
    model = WPCategory
    list_display = ("name", "slug", "parent", "wp_id", "taxonomy")
    list_filter = ("taxonomy", "parent")
    search_fields = ("name",)
    add_to_admin_menu = False


wp_category_url_helper = WPCategoryAdmin().url_helper

modeladmin_register(WPCategoryAdmin)


class WPTagAdmin(ModelAdmin):
    model = WPTag
    list_display = ("name", "slug", "wp_id")
    search_fields = ("name",)
    add_to_admin_menu = False


wp_tag_url_helper = WPTagAdmin().url_helper

modeladmin_register(WPTagAdmin)


class WPAuthorAdmin(ModelAdmin):
    model = WPAuthor
    list_display = ("name", "slug", "wp_id")
    search_fields = ("name",)
    add_to_admin_menu = False


wp_author_url_helper = WPAuthorAdmin().url_helper

modeladmin_register(WPAuthorAdmin)


class WPPostAdmin(ModelAdmin):
    model = WPPost
    list_display = ("title", "wp_id")
    search_fields = ("title",)
    add_to_admin_menu = False


wp_post_url_helper = WPPostAdmin().url_helper

modeladmin_register(WPPostAdmin)


@hooks.register("register_admin_urls")
def register_import_wordpress_data_url():
    return [
        path(
            "import-wordpress-data/",
            import_wordpress_data_view,
            name="import_wordpress_data",
        ),
        path(
            "run_import/",
            run_import,
            name="run_import",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_import_wordpress_data_menu_item():
    submenu = Menu(
        items=[
            MenuItem(
                "WP Categories", wp_category_url_helper.index_url, icon_name="table"
            ),
            MenuItem("WP Tags", wp_tag_url_helper.index_url, icon_name="table"),
            MenuItem("WP Authors", wp_author_url_helper.index_url, icon_name="table"),
            MenuItem("WP Posts", wp_post_url_helper.index_url, icon_name="table"),
            MenuItem(
                "Import Data", reverse("import_wordpress_data"), icon_name="download"
            ),
        ]
    )

    return SubmenuMenuItem("WP Importer", submenu, icon_name="download-alt")


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
