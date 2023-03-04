from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class AbstractPage(Page):
    """
    Abstract page model for all app page models that
    will be created from imported wordpress data.
    """

    content = RichTextField(blank=True)
    excerpt = RichTextField(blank=True)

    panels = [
        FieldPanel("content"),
        FieldPanel("excerpt"),
    ]

    class Meta:
        abstract = True
