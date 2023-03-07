from django.apps import apps
from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel

from wagtail_toolbox.wordpress.utils import get_model_mapping


class WordpressModel(models.Model):
    """ABSTRACT Base model for Wordpress models that will be imported."""

    SOURCE_URL = None  # e.g. /wp-json/wp/v2/[model_name]

    def __init__(self, *args, **kwargs):
        """Set the source URL."""
        if not self.SOURCE_URL:
            raise NotImplementedError("WordpressModel must have a SOURCE_URL attribute")

        super().__init__(*args, **kwargs)

    wp_id = models.IntegerField(unique=True, verbose_name="Wordpress ID")
    wp_foreign_keys = models.JSONField(blank=True, null=True)
    wp_many_to_many_keys = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_source_url(self):
        """Get the source URL for the Wordpress object."""
        return self.SOURCE_URL.strip("/")

    def exclude_fields_initial_import(self):
        """Fields to exclude from the initial import."""
        exclude_foreign_keys = []
        for field in self.process_foreign_keys():
            for key, _ in field.items():
                exclude_foreign_keys.append(key)
            # exclude_foreign_keys.append(list(field.keys())[0])
        # print(exclude_foreign_keys)

        exclude_many_to_many_keys = []
        for field in self.process_many_to_many_keys():
            for key, _ in field.items():
                exclude_many_to_many_keys.append(key)
        # print(exclude_many_to_many_keys)
        # #     print(field)
        # #     exclude_many_to_many_keys.append(list(field.keys())[0])

        return exclude_foreign_keys + exclude_many_to_many_keys

    @staticmethod
    def process_foreign_keys():
        """Override this method to process foreign keys."""
        return []

    @staticmethod
    def process_many_to_many_keys():
        """Override this method to process many to many keys."""
        return []

    @staticmethod
    def process_fields():
        """Override this method to process fields."""
        return []

    @staticmethod
    def transfer_data(model, queryset):
        """Transfer data from the source model to the target model."""

        config = get_model_mapping(model.SOURCE_URL)
        source_model = apps.get_model(
            app_label=config["source_model"][0], model_name=config["source_model"][1]
        )
        target_model = apps.get_model(
            app_label=config["target_model"][0], model_name=config["target_model"][1]
        )
        results = {
            "created": 0,
            "updated": 0,
        }
        exclude_fields = [
            "id",
            "wp_id",
            "wp_foreign_keys",
            "wp_many_to_many_keys",
        ]
        field_mapping = (
            config["field_mapping"] if hasattr(config, "field_mapping") else []
        )

        if not field_mapping:
            # copy across all fields where the target has a matching field

            # get fields from target model
            fields = target_model._meta.get_fields()
            field_names = [
                field.name for field in fields if field.name not in exclude_fields
            ]

            for obj in queryset:
                source_obj = source_model.objects.get(wp_id=obj.wp_id)
                values = {}
                for field_name in field_names:
                    if hasattr(source_obj, field_name):
                        values[field_name] = getattr(source_obj, field_name)
                _, created = target_model.objects.get_or_create(**values)
                if created:
                    results["created"] += 1
                else:
                    results["updated"] += 1
            results["total"] = results["created"] + results["updated"]
            results["model"] = target_model._meta.verbose_name_plural

        else:
            # copy across fields defined in the field mapping

            for obj in queryset:
                source_obj = source_model.objects.get(wp_id=obj.wp_id)
                values = {}
                for field_name in config["field_mapping"]:
                    if hasattr(source_obj, field_name[0]):
                        values[field_name[1]] = getattr(source_obj, field_name[0])
                _, created = target_model.objects.get_or_create(**values)
                if created:
                    results["created"] += 1
                else:
                    results["updated"] += 1
            results["total"] = results["created"] + results["updated"]
            results["model"] = target_model._meta.verbose_name_plural

        return results


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
    taxonomy = models.CharField(max_length=255)

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
        FieldPanel("wp_many_to_many_keys"),
    ]

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

    panels = [
        FieldPanel("name"),
        FieldPanel("link"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldRowPanel(
            [
                # FieldPanel("parent"),
                FieldPanel("taxonomy"),
                FieldPanel("count"),
            ]
        ),
        FieldPanel("wp_id"),
        FieldPanel("wp_foreign_keys"),
        FieldPanel("wp_many_to_many_keys"),
    ]


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

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
        FieldPanel("link"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("avatar_urls"),
        FieldPanel("wp_id"),
        FieldPanel("wp_foreign_keys"),
        FieldPanel("wp_many_to_many_keys"),
    ]


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
    author = models.ForeignKey(
        WPAuthor, on_delete=models.SET_NULL, blank=True, null=True
    )
    categories = models.ManyToManyField(WPCategory, blank=True)
    tags = models.ManyToManyField(WPTag, blank=True)

    # featured_media = models.IntegerField(default=0)
    comment_status = models.CharField(max_length=255)
    ping_status = models.CharField(max_length=255)
    sticky = models.BooleanField(default=False)
    format = models.CharField(max_length=255)
    template = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    panels = [
        FieldPanel("title"),
        FieldRowPanel(
            [
                FieldPanel("date"),
                FieldPanel("date_gmt"),
            ]
        ),
        FieldPanel("guid"),
        FieldRowPanel(
            [
                FieldPanel("modified"),
                FieldPanel("modified_gmt"),
            ]
        ),
        FieldPanel("slug"),
        FieldRowPanel(
            [
                FieldPanel("status"),
                FieldPanel("type"),
                FieldPanel("link"),
            ]
        ),
        FieldPanel("content"),
        FieldPanel("excerpt"),
        FieldRowPanel(
            [
                FieldPanel("author"),
                FieldPanel("categories"),
                FieldPanel("tags"),
            ]
        ),
        FieldRowPanel(
            [
                FieldPanel("comment_status"),
                FieldPanel("ping_status"),
                FieldPanel("sticky"),
                FieldPanel("format"),
                FieldPanel("template"),
            ]
        ),
        FieldPanel("wp_id"),
        FieldPanel("wp_foreign_keys"),
        FieldPanel("wp_many_to_many_keys"),
    ]

    @staticmethod
    def process_foreign_keys():
        """These are excluded from the first import and processed later."""
        return [
            {
                "author": {"model": "WPAuthor", "field": "wp_id"},
            }
        ]

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
    author = models.ForeignKey(
        WPAuthor, on_delete=models.SET_NULL, blank=True, null=True
    )
    # categories = models.ManyToManyField(WPCategory, blank=True)
    # tags = models.ManyToManyField(WPTag, blank=True)

    # featured_media = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "wordpress.WPPage", on_delete=models.SET_NULL, blank=True, null=True
    )
    comment_status = models.CharField(max_length=255)
    ping_status = models.CharField(max_length=255)
    sticky = models.BooleanField(default=False)
    # format = models.CharField(max_length=255)
    template = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title

    panels = [
        FieldPanel("title"),
        FieldRowPanel([FieldPanel("date"), FieldPanel("date_gmt")]),
        FieldPanel("guid"),
        FieldRowPanel([FieldPanel("modified"), FieldPanel("modified_gmt")]),
        FieldPanel("slug"),
        FieldRowPanel(
            [
                FieldPanel("status"),
                FieldPanel("type"),
                FieldPanel("link"),
                FieldPanel("parent"),
            ]
        ),
        FieldPanel("content"),
        FieldPanel("excerpt"),
        FieldRowPanel(
            [
                FieldPanel("author"),
                FieldPanel("comment_status"),
                FieldPanel("ping_status"),
                FieldPanel("sticky"),
                FieldPanel("template"),
            ]
        ),
        FieldPanel("wp_id"),
        FieldPanel("wp_foreign_keys"),
        FieldPanel("wp_many_to_many_keys"),
    ]

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

    post = models.ForeignKey(WPPost, on_delete=models.CASCADE, blank=True, null=True)
    parent = models.ForeignKey(
        "wordpress.WPComment", on_delete=models.CASCADE, blank=True, null=True
    )
    # not sure if this is needed as they all seem to be zero
    author = models.ForeignKey(
        WPAuthor, on_delete=models.SET_NULL, blank=True, null=True
    )
    author_name = models.CharField(max_length=255)
    author_url = models.URLField()
    date = models.DateTimeField()
    date_gmt = models.DateTimeField()
    content = models.TextField(blank=True, null=True)
    link = models.URLField()
    status = models.CharField(
        max_length=255, null=True, blank=True
    )  # TODO: check if this should be boolean
    type = models.CharField(max_length=255)
    author_avatar_urls = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.author_name

    panels = [
        FieldPanel("post"),
        FieldPanel("parent"),
        FieldPanel("author"),
        FieldPanel("author_name"),
        FieldPanel("author_url"),
        FieldRowPanel([FieldPanel("date"), FieldPanel("date_gmt")]),
        FieldPanel("content"),
        FieldPanel("link"),
        FieldPanel("status"),
        FieldPanel("type"),
        FieldPanel("author_avatar_urls"),
    ]

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
    author = models.ForeignKey(
        "wordpress.WPAuthor", on_delete=models.SET_NULL, blank=True, null=True
    )
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
    post = models.ForeignKey(
        "wordpress.WPPost", on_delete=models.CASCADE, blank=True, null=True
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

    panels = [
        FieldPanel("title"),
        FieldRowPanel([FieldPanel("date"), FieldPanel("date_gmt")]),
        FieldPanel("guid"),
        FieldRowPanel([FieldPanel("modified"), FieldPanel("modified_gmt")]),
        FieldPanel("slug"),
        FieldRowPanel(
            [
                FieldPanel("author"),
                FieldPanel("status"),
                FieldPanel("type"),
                FieldPanel("link"),
            ]
        ),
        FieldPanel("description"),
        FieldPanel("caption"),
        FieldPanel("alt_text"),
        FieldPanel("media_type"),
        FieldPanel("mime_type"),
        FieldPanel("source_url"),
        FieldPanel("post"),
    ]
