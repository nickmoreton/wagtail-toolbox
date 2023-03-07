import logging

import requests
from django.conf import settings
from wagtail.models import Page


def parse_wordpress_routes(host):
    """
    Parses the wordpress routes.

    Returns:
        list: A sorted list of dicts with the route and the model name etc.

    Args:
        host (str): The host url.
    """

    try:
        resp = requests.get(host + "/wp-json/", timeout=3)
    except requests.exceptions.ConnectionError:
        logging.warning("Could not connect to wordpress host")
        return []

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
    url = "/wordpress-import-admin/wordpress/" + model_name + "/"
    return url


def get_model_mapping(source):
    if hasattr(settings, "WP_IMPORTER_MODEL_MAPPING"):
        source = source.split("/")[-1]
        model_mapping = settings.WP_IMPORTER_MODEL_MAPPING.get(source, None)
        return model_mapping


def get_page_model_fields():
    """
    Get the fields for the page model.

    Returns:
        list: A list of field names.
    """
    page_model = Page()
    return [field.name for field in page_model._meta.get_fields()]
