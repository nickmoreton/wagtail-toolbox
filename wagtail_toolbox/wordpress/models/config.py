# from django import forms
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, HelpPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable, ParentalKey

# class EndpointSelectWidget(forms.Select):
#     def __init__(self, attrs=None, choices=()):
#         super().__init__(attrs, choices)
#         self.attrs["onchange"] = "set_endpoint_url_model(this)"

#     class Media:
#         js = ("wordpress/js/endpoint_select.js",)


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
            <p class="help-block help-info">
            <svg class="icon icon-help icon" aria-hidden="true"><use href="#icon-help"></use></svg>
            Each endpoint added here will be available in the Import Data admin page.<p>
            """,
            heading="Help",
        ),
        InlinePanel(
            "wordpress_endpoints", heading="JSON API Endpoints.", label="Endpoint"
        ),
    ]
