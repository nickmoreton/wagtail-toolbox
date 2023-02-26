import requests
from django import forms
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, HelpPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable

from wagtail_toolbox.wordpress.panels import EndpointSelectPanel


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


@register_setting
class WordpressSettings(ClusterableModel, BaseSiteSetting):
    """Settings for the Wordpress importer."""

    host = models.URLField(null=True, verbose_name="Source Site Host URL")

    panels = [
        FieldPanel("host"),
        HelpPanel(
            """<p>JSON API endpoints will be fetched from the host URL in the order they are listed below.</p>
            <p>Some imports need to happen before other imports due to related content.</p>""",
            heading="Help",
        ),
        InlinePanel("endpoints", heading="JSON API Endpoints", label="Endpoint"),
    ]

    def clean(self):
        """Validate the host is a valid URL and response."""
        super().clean()
        if self.host:
            try:
                resp = requests.get(self.host)
                if resp.status_code != 200:
                    raise forms.ValidationError("Host should be the base URL")
            except requests.exceptions.ConnectionError:
                raise forms.ValidationError("Host URL is not reachable")

    def get_endpoints(self):
        """Get the endpoints from the database."""
        return {
            "endpoints": [self.endpoints.all().values("name", "url", "model")],
        }
