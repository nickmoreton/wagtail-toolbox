from django import template

from wagtail_toolbox.wordpress.utils import get_django_model_admin_url as get_url

register = template.Library()


@register.simple_tag
def get_model_admin_url(model_name):
    """
    Get the admin url for a given model name.

    Args:
        model_name (str): The model name.

    Returns:
        str: The admin url.
    """
    return get_url(model_name)
