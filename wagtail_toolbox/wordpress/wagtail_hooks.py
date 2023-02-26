import json

from wagtail import hooks

from .panels import wordpress_routes


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
