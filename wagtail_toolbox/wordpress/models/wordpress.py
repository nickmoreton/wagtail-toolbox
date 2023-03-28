from bs4 import BeautifulSoup as bs4
from django.conf import settings
from django.db import models


class WordpressModel(models.Model):
    """ABSTRACT Base model for the Wordpress models.

    All Wordpress models should inherit from this model.
    """

    # Format: /wp-json/wp/v2/[model_name]
    # This is passed to the wordpress client and appended to WP_HOST
    # It's required on every wordpress model
    SOURCE_URL = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.SOURCE_URL:
            raise NotImplementedError("WordpressModel must have a SOURCE_URL attribute")

    wp_id = models.IntegerField(unique=True, verbose_name="Wordpress ID")
    wp_foreign_keys = models.JSONField(blank=True, null=True)
    wp_many_to_many_keys = models.JSONField(blank=True, null=True)
    wagtail_model = models.JSONField(blank=True, null=True)
    wp_cleaned_content = models.TextField(blank=True, null=True)
    wp_block_content = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def get_title(self):
        """Get the title for the Wordpress object
        either name or title depending on the model."""
        return self.title if hasattr(self, "title") else self.name

    def exclude_fields_initial_import(self):
        """Fields to exclude from the initial import."""
        exclude_foreign_keys = []
        for field in self.process_foreign_keys():
            for key, _ in field.items():
                exclude_foreign_keys.append(key)

        exclude_many_to_many_keys = []
        for field in self.process_many_to_many_keys():
            for key, _ in field.items():
                exclude_many_to_many_keys.append(key)

        return exclude_foreign_keys + exclude_many_to_many_keys

    @staticmethod
    def clean_content_html(html_content, clean_tags=None):
        """Clean the content.

        Args:
            content (str): The content to clean.
            clean_tags (list): A list of tags to clean.

        Returns:
            str: The cleaned content.
        """
        if not clean_tags:
            clean_tags = getattr(settings, "WPI_CLEAN_TAGS", ["div"])

        if html_content:
            soup = bs4(html_content, "html.parser")
            # find all clean_tags tag name and remove them while keeping their contents
            for div in soup.find_all(clean_tags):
                div.unwrap()
            html_content = str(soup)

        return html_content

    @staticmethod
    def process_fields():
        """Override this method to process fields."""
        return []

    @staticmethod
    def process_foreign_keys():
        """Override this method to process foreign keys."""
        return []

    @staticmethod
    def process_many_to_many_keys():
        """Override this method to process many to many keys."""
        return []

    @staticmethod
    def process_clean_fields():
        """Override this method to process content by cleaning it."""
        return []

    @staticmethod
    def process_block_fields():
        """Override this method to process content by building blocks."""
        return []

    def get_source_url(self):
        """Get the source URL for the Wordpress object."""
        return self.SOURCE_URL.strip("/")


clean_html = WordpressModel.clean_content_html  # for convenience


class WPCategory(WordpressModel):
    """Model definition for Category."""

    SOURCE_URL = "/wp-json/wp/v2/categories"

    name = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    link = models.URLField()
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    taxonomy = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "wordpress.WPCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return [
            {
                "parent": {"model": "self", "field": "wp_id"},
            }
        ]


class WPTag(WordpressModel):
    """Model definition for Tags."""

    SOURCE_URL = "/wp-json/wp/v2/tags"
    UNIQUE_FIELDS = ["name"]

    name = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    link = models.URLField()
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    taxonomy = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class WPAuthor(WordpressModel):
    """Model definition for Author. AKA User."""

    SOURCE_URL = "/wp-json/wp/v2/users"

    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField()
    slug = models.SlugField()
    avatar_urls = models.URLField(blank=True, null=True)  # comes from avatar_urls.96

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.name


class WPPost(WordpressModel):
    """Model definition for Post."""

    SOURCE_URL = "/wp-json/wp/v2/posts"

    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    date_gmt = models.DateTimeField()
    guid = models.URLField()
    modified = models.DateTimeField()
    modified_gmt = models.DateTimeField()
    slug = models.SlugField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    link = models.URLField()
    content = models.TextField(blank=True, null=True)
    excerpt = models.TextField(blank=True, null=True)
    comment_status = models.CharField(max_length=255)
    ping_status = models.CharField(max_length=255)
    sticky = models.BooleanField(default=False)
    format = models.CharField(max_length=255)
    template = models.CharField(max_length=255, null=True, blank=True)
    author = models.ForeignKey(
        WPAuthor,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(
        WPCategory,
        blank=True,
    )
    tags = models.ManyToManyField(
        WPTag,
        blank=True,
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return [{"author": {"model": "WPAuthor", "field": "wp_id"}}]

    @staticmethod
    def process_many_to_many_keys():
        """These are excluded from the first import and processed later."""
        return [
            {
                "categories": {"model": "WPCategory", "field": "wp_id"},
                "tags": {"model": "WPTag", "field": "wp_id"},
            }
        ]

    @staticmethod
    def process_fields():
        """The value is from other keys of the incoming data."""
        return [
            {"title": "title.rendered"},
            {"content": "content.rendered"},
            {"excerpt": "excerpt.rendered"},
            {"guid": "guid.rendered"},
        ]

    @staticmethod
    def process_clean_fields():
        """Clean the content."""
        return [
            {
                "content": "wp_cleaned_content",
            }
        ]

    @staticmethod
    def process_block_fields():
        """Process the content into blocks."""
        return [
            {
                "wp_cleaned_content": "wp_block_content",
            }
        ]


class WPPage(WordpressModel):
    """Model definition for Page."""

    SOURCE_URL = "/wp-json/wp/v2/pages"

    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    date_gmt = models.DateTimeField()
    guid = models.URLField()
    modified = models.DateTimeField()
    modified_gmt = models.DateTimeField()
    slug = models.SlugField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    link = models.URLField()
    content = models.TextField(blank=True, null=True)
    excerpt = models.TextField(blank=True, null=True)
    comment_status = models.CharField(max_length=255)
    ping_status = models.CharField(max_length=255)
    sticky = models.BooleanField(default=False)
    template = models.CharField(max_length=255, null=True, blank=True)
    author = models.ForeignKey(
        "wordpress.WPAuthor",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        "wordpress.WPPage",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return [
            {
                "author": {"model": "WPAuthor", "field": "wp_id"},
                "parent": {"model": "WPPage", "field": "wp_id"},
            }
        ]

    @staticmethod
    def process_fields():
        """The value is from other keys of the incoming data."""
        return [
            {"title": "title.rendered"},
            {"content": "content.rendered"},
            {"excerpt": "excerpt.rendered"},
            {"guid": "guid.rendered"},
        ]


class WPComment(WordpressModel):
    """Model definition for Comment."""

    SOURCE_URL = "/wp-json/wp/v2/comments"

    author_name = models.CharField(max_length=255)
    author_url = models.URLField()
    date = models.DateTimeField()
    date_gmt = models.DateTimeField()
    content = models.TextField(blank=True, null=True)
    link = models.URLField()
    status = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255)
    author_avatar_urls = models.URLField(blank=True, null=True)
    post = models.ForeignKey(
        "wordpress.WPPost",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        "wordpress.WPComment",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    # is this needed as they all seem to be zero anyway?
    author = models.ForeignKey(
        "wordpress.WPAuthor",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.author_name

    @staticmethod
    def process_fields():
        """The value is from other keys of the incoming data."""
        return [
            {"content": "content.rendered"},
        ]

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return [
            {
                "post": {"model": "WPPost", "field": "wp_id"},
                "parent": {"model": "WPComment", "field": "wp_id"},
                "author": {"model": "WPAuthor", "field": "wp_id"},
            }
        ]


class WPMedia(WordpressModel):
    """Model definition for Media."""

    SOURCE_URL = "/wp-json/wp/v2/media"

    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    date_gmt = models.DateTimeField()
    guid = models.URLField()
    modified = models.DateTimeField()
    modified_gmt = models.DateTimeField()
    slug = models.SlugField()
    status = models.CharField(max_length=255)
    comment_status = models.CharField(max_length=255)
    ping_status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    link = models.URLField()
    template = models.CharField(max_length=255)
    description = models.TextField()
    caption = models.TextField()
    alt_text = models.CharField(max_length=255)
    media_type = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255)
    source_url = models.URLField()
    author = models.ForeignKey(
        "wordpress.WPAuthor",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    post = models.ForeignKey(
        "wordpress.WPPost",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"

    def __str__(self):
        return self.title

    @staticmethod
    def process_fields():
        """The value is from other keys of the incoming data."""
        return [
            {"description": "description.rendered"},
            {"caption": "caption.rendered"},
            {"title": "title.rendered"},
            {"guid": "guid.rendered"},
        ]

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return [
            {
                "author": {"model": "WPAuthor", "field": "wp_id"},
                "post": {"model": "WPPost", "field": "wp_id"},
            }
        ]
