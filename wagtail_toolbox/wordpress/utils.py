from django.apps import apps


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


def get_model_type(config):
    """Deal with save actions differently for wagtail pages vs django models
    e.g. some saves are to django models, some are to wagtail pages"""

    model_type = (
        "page"
        if "model_type" in config.keys() and config["model_type"] == "page"
        else "model"
    )

    return model_type


def get_many_to_many_mapping(config):
    """Get the many to many mapping from the config"""
    return config.get("many_to_many_mapping", [])


def get_related_mapping(config):
    """Get the related mapping from the config"""
    return config.get("related_mapping", [])


def get_target_model(config):
    """Get the target model from the config"""
    return apps.get_model(
        app_label=config["target_model"][0],
        model_name=config["target_model"][1],
    )


def make_signature(soup):
    """Make a signature for a soup object.

    params:
        html (str): The html snippet to make a signature for.

    returns:
        str: The ':' separated signature for the html snippet
    """
    signature = ""
    for tag in soup.findChildren(recursive=True):
        print(tag)
        tag_pattern = f"{tag.name}:"
        current = tag.find()
        while current and current.findChildren(recursive=False):
            tag_pattern += f"{current.name}:"
            current = current.find()
    return signature
