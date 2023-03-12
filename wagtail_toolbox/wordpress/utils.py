import logging

import requests
from django.apps import apps
from django.conf import settings


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

    if hasattr(settings, "WPI_EXCLUDE_ROUTES"):
        trimmed_routes = []
        for route in routes:
            for key, _ in route.items():
                if key not in settings.WPI_EXCLUDE_ROUTES:
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


def get_target_mapping(source):
    if hasattr(settings, "WPI_TARGET_MAPPING"):
        source = source.split("/")[-1]
        model_mapping = settings.WPI_TARGET_MAPPING.get(source, None)
        return model_mapping


def get_model_type(config):
    """Deal with save actions differently for wagtail pages vs django models"""

    model_type = (
        "page"
        if "model_type" in config.keys() and config["model_type"] == "page"
        else "model"
    )

    return model_type


def check_transfer_available():
    if not hasattr(settings, "WPI_TARGET_BLOG_INDEX"):
        return False
    if not settings.WPI_TARGET_BLOG_INDEX[0] or not settings.WPI_TARGET_BLOG_INDEX[1]:
        return False
    blog_indexPage = apps.get_model(
        settings.WPI_TARGET_BLOG_INDEX[0], settings.WPI_TARGET_BLOG_INDEX[1]
    ).objects.first()
    if blog_indexPage:
        return True


# def get_many_to_many_mapping(config):
#     """Get the many to many mapping from the config"""
#     return config.get("many_to_many_mapping", None)


# def get_related_mapping(config):
#     """Get the related mapping from the config"""
#     return config.get("related_mapping", None)


def get_target_model(config):
    """Get the target model from the config"""
    return apps.get_model(
        app_label=config["target_model"][0],
        model_name=config["target_model"][1],
    )
