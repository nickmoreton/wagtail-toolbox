import requests
from django.conf import settings


def parse_wordpress_routes(host):
    """
    Parses the wordpress routes.

    Returns:
        list: A sorted list of dicts with the route and the model name etc.

    Args:
        host (str): The host url.
    """

    resp = requests.get(host + "/wp-json/")
    if resp.status_code != 200:
        raise Exception("Could not get wordpress routes")
    routes = [
        {
            "wp-json"
            + route: {
                "host": value.get("_links")["self"][0]["href"],
                "name": route.split("/")[-1],
                "model": "WP" + route.split("/")[-1].capitalize(),
            }
        }
        for route, value in resp.json()["routes"].items()
        if value["namespace"] == "wp/v2"
        and (value["methods"] == ["GET", "POST"] or value["methods"] == ["GET"])
        and len(route.split("/")) == 4  # only get the top level routes
    ]

    if hasattr(settings, "WP_IMPORTER_EXCLUDE"):
        trimmed_routes = []
        for route in routes:
            for key, _ in route.items():
                if key not in settings.WP_IMPORTER_EXCLUDE:
                    trimmed_routes.append(route)
        routes = trimmed_routes

    return sorted(routes, key=lambda x: list(x.keys())[0])


def get_django_model_admin_url(model_name):
    """
    Get the admin url for a given model name.

    Args:
        model_name (str): The model name.

    Returns:
        str: The admin url.
    """
    print(model_name)
    url = "/wordpress-import-admin/wordpress/" + model_name + "/"
    return url
