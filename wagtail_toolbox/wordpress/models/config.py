from django import forms
from django.conf import settings
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, HelpPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable, ParentalKey

from wagtail_toolbox.wordpress.utils import parse_wordpress_routes


class EndpointSelectWidget(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
        self.attrs["onchange"] = "set_endpoint_url_model(this)"

    class Media:
        js = ("wordpress/js/endpoint_select.js",)


class EndpointSelectPanel(FieldPanel):
    def __init__(self, field_name, **kwargs):
        super().__init__(field_name, **kwargs)
        choices = (("", "---------"),)
        for route in parse_wordpress_routes(settings.WP_IMPORTER_HOST):
            for _, value in route.items():
                choices += ((value["name"], value["name"]),)

        self.widget = EndpointSelectWidget(choices=choices)


class Endpoint(Orderable):
    name = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255, unique=True)
    model = models.CharField(max_length=255, unique=True)
    setting = ParentalKey("WordpressSettings", related_name="endpoints")

    panels = [
        EndpointSelectPanel(
            "name"
        ),  # renders a select with the options from the wordpress_routes function
        FieldPanel("url"),
        FieldPanel("model"),
    ]


@register_setting(icon="cogs")
class WordpressSettings(ClusterableModel, BaseSiteSetting):
    """Settings for the Wordpress importer."""

    panels = [
        HelpPanel(
            f"""
            <p>JSON API endpoints will be fetched from {settings.WP_IMPORTER_HOST} in
            the order they are listed below.</p>
            <p>Some imports need to happen before other imports due to related content.</p>
            """,
            heading="Help",
        ),
        InlinePanel("endpoints", heading="JSON API Endpoints", label="Endpoint"),
    ]

    def get_endpoints(self):
        """Get the endpoints from the database."""
        return self.endpoints.all()

    def get_host(self):
        """Get the host from the database."""
        return settings.WP_IMPORTER_HOST