from django import template
from django.utils.module_loading import import_string

register = template.Library()


@register.simple_tag
def get_model_admin_url(model_name):
    normal = "wp_" + model_name.lower().strip("wp") + "_url_helper"
    helper = import_string("wagtail_toolbox.wordpress.wagtail_hooks." + normal)
    url = helper.index_url
    return url
