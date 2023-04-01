from django import forms
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, HelpPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable, ParentalKey


class EndpointSelectWidget(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
        self.attrs["onchange"] = "set_endpoint_url_model(this)"

    class Media:
        js = ("wordpress/js/endpoint_select.js",)


class StreamBlockSignatureBlocks(models.Model):
    """Store the signatures for the HTML blocks."""

    signature = models.CharField(max_length=255, unique=True)
    block_name = models.CharField(max_length=255)
    block_kwargs = models.JSONField(blank=True, null=True)
    model = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.signature

    class Meta:
        verbose_name_plural = "Stream Block Signature Blocks"
        ordering = ["signature"]


class WordpressEndpoint(Orderable):
    name = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255, unique=True)
    model = models.CharField(max_length=255, unique=True)
    setting = ParentalKey("WordpressHost", related_name="wordpress_endpoints")

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
        FieldPanel("model"),
    ]


@register_setting(icon="cogs")
class WordpressHost(ClusterableModel, BaseSiteSetting):
    """Settings for the Wordpress importer."""

    panels = [
        HelpPanel(
            """
            JSON API endpoints will be fetched from your wordpress host in the order they are listed below.
            <div class="help-block help-warning">
            <svg class="icon icon-warning icon" aria-hidden="true"><use href="#icon-warning"></use></svg>
            Some imports need to happen before other imports due to related content.
            </div>
            """,
            heading="Help",
        ),
        InlinePanel(
            "wordpress_endpoints", heading="JSON API Endpoints", label="Endpoint"
        ),
    ]

    def get_endpoints(self):
        """Get the endpoints from the database."""
        return self.wordpress_endpoints.all()
