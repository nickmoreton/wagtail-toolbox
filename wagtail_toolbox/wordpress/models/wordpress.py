from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel

class WordpressModel(models.Model):
    """Base model for Wordpress models that will be imported."""

    SOURCE_URL = None # e.g. /wp-json/wp/v2/[model_name]

    def __init__(self, *args, **kwargs):
        """Set the source URL."""
        if not self.SOURCE_URL:
            raise NotImplementedError("WordpressModel must have a SOURCE_URL attribute")
        
        super().__init__(*args, **kwargs)

    wp_id = models.IntegerField(unique=True, verbose_name="Wordpress ID")
    wp_foreign_keys = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_source_url(self):
        """Get the source URL for the Wordpress object."""
        return self.SOURCE_URL.strip("/")


class WPTaxonomy(models.Model):
    """Model definition for FixtureTaxonomy."""

    name = models.CharField(max_length=255)  # nice name for the taxonomy
    slug = models.SlugField()  # slug for the taxonomy used for the foreign key lookup

    class Meta:
        verbose_name = "Taxonomy"
        verbose_name_plural = "Taxonomies"

    def __str__(self):
        return self.name


class WPCategory(WordpressModel):
    """Model definition for Category."""

    SOURCE_URL = "/wp-json/wp/v2/categories"

    name = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    link = models.URLField()
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "wordpress.WPCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    taxonomy = models.ForeignKey(
        "wordpress.WPTaxonomy",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("link"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldRowPanel(
            [
                FieldPanel("parent"),
                FieldPanel("taxonomy"),
                FieldPanel("count"),
            ]
        ),
        FieldPanel("wp_id"),
        FieldPanel("wp_foreign_keys"),
    ]

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return {
            "parent": {"model": "category", "field": "wp_id"},
            "taxonomy": {"model": "taxonomy", "field": "slug"},
        }

    @staticmethod
    def exclude_fields_initial_import():
        """These fields are excluded from the initial import."""
        return WPCategory.process_foreign_keys().keys()
