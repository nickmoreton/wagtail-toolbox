# from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe

from wagtail_toolbox.wordpress.models import (
    WPAuthor,
    WPCategory,
    WPComment,
    WPMedia,
    WPPage,
    WPPost,
    WPTag,
)

# from wagtail_toolbox.wordpress.utils import get_model_mapping


class WordpressImportAdminSite(admin.AdminSite):
    # Admin site for the imported wordpress data
    site_header = "Wordpress Import Admin"
    site_title = "Wordpress Import Admin Portal"
    index_title = "Welcome to the Wordpress Import Admin Portal"


wordpress_import_admin_site = WordpressImportAdminSite(name="wordpress-import-admin")


class BaseAdmin(admin.ModelAdmin):
    """
    Base admin class for all wordpress models

    This class provides some common functionality for all wordpress models.
    It's main purpose is to keep the admin list_display pages clean and easy to read.
    """

    actions = ["transfer_data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(settings, "WP_IMPORTER_TRUNCATE_LENGTH"):
            self.truncated_length = 12
        else:
            self.truncated_length = settings.WP_IMPORTER_TRUNCATE_LENGTH

        first_fields = ["name", "title", "author_name"]
        last_fields = ["wp_id", "wp_foreign_keys", "wp_many_to_many_keys"]

        truncated_fields = [
            "title",
            "name",
            "content",
            "excerpt",
            "description",
            "caption",
        ]

        remove_fields = [
            "wp_foreign_keys",
            "wp_many_to_many_keys",
            "author_avatar_urls",
            "avatar_urls",
        ]

        link_fields = ["guid", "link", "source_url"]

        self.list_display = self.get_list_display_fields(
            self.model,
            remove_fields,
            first_fields,
            last_fields,
            truncated_fields,
            link_fields,
        )
        self.search_fields = [
            field.name
            for field in self.model._meta.fields
            if field.name in first_fields
        ]

    def get_list_display_fields(
        self,
        obj,
        remove_fields,
        first_fields,
        last_fields,
        truncated_fields,
        link_fields,
    ):
        """
        Return the list_display fields for a model

        This method is used to add some common functionality to the admin list_display pages.

        1. add some column ordering
        2. truncate some overly long fields
        3. remove some fields
        4. add some links to open the original wordpress content
        """
        fields = sorted([field.name for field in obj._meta.fields])

        for field in first_fields:
            if field in fields:
                fields.remove(field)
                fields.insert(0, field)

        for field in last_fields:
            if field in fields:
                fields.remove(field)
                fields.append(field)

        for field in truncated_fields:
            if field in fields:
                position = fields.index(field)
                fields.insert(position, f"get_truncated_{field}")
                fields.remove(field)

        for field in remove_fields:
            if field in fields:
                fields.remove(field)

        for field in link_fields:
            if field in fields:
                position = fields.index(field)
                fields.insert(position, f"get_link_{field}")
                fields.remove(field)

        return fields

    def get_truncated_content(self, obj):
        return (
            obj.content[: self.truncated_length] + "..."
            if len(obj.content) > self.truncated_length
            else obj.content
        )

    get_truncated_content.short_description = "Content"

    def get_truncated_excerpt(self, obj):
        return (
            obj.excerpt[: self.truncated_length] + "..."
            if len(obj.excerpt) > self.truncated_length
            else obj.excerpt
        )

    get_truncated_excerpt.short_description = "Excerpt"

    def get_truncated_description(self, obj):
        return (
            obj.description[: self.truncated_length] + "..."
            if len(obj.description) > self.truncated_length
            else obj.description
        )

    get_truncated_description.short_description = "Description"

    def get_truncated_caption(self, obj):
        return (
            obj.caption[: self.truncated_length] + "..."
            if len(obj.caption) > self.truncated_length
            else obj.caption
        )

    get_truncated_caption.short_description = "Caption"

    def get_truncated_title(self, obj):
        return (
            obj.title[: self.truncated_length] + "..."
            if len(obj.title) > self.truncated_length
            else obj.title
        )

    get_truncated_title.short_description = "Title"

    def get_truncated_name(self, obj):
        return (
            obj.name[: self.truncated_length] + "..."
            if len(obj.name) > self.truncated_length
            else obj.name
        )

    get_truncated_name.short_description = "Name"

    def get_link_guid(self, obj):
        guid = obj.guid
        guid = f'<a href="{guid}" target="_blank">Open</a>'
        return mark_safe(guid)

    get_link_guid.short_description = "Guid"

    def get_link_link(self, obj):
        link = obj.link
        link = f'<a href="{link}" target="_blank">Open</a>'
        return mark_safe(link)

    get_link_link.short_description = "Link"

    def get_link_source_url(self, obj):
        source_url = obj.source_url
        source_url = f'<a href="{source_url}" target="_blank">Open</a>'
        return mark_safe(source_url)

    get_link_source_url.short_description = "Source Url"

    def transfer_data(self, request, queryset):
        """
        Transfer data from wordpress to wagtail models
        """

        wp_model_class = queryset[0].instance.__class__
        print(wp_model_class).__class__
        # config = get_model_mapping(self.SOURCE_URL)
        # source_model = apps.get_model(
        #     app_label=config["app_label"],
        #     model_name=config["model_name"],
        # )
        # target_model = apps.get_model(
        #     app_label=config["app_label"],
        #     model_name=config["target_model_name"],
        # )
        # field_mapping = config["fields_mapping"]

        # if field_mapping:
        #     # use the field mapping to transfer data
        #     print("Using field mapping")
        #     return

        # # transfer all fields
        # # the field names must match between models

        # print("Transferring data for {}".format(self.SOURCE_URL)) if config else None


wordpress_import_admin_site.register(WPPage, BaseAdmin)
wordpress_import_admin_site.register(WPCategory, BaseAdmin)
wordpress_import_admin_site.register(WPTag, BaseAdmin)
wordpress_import_admin_site.register(WPAuthor, BaseAdmin)
wordpress_import_admin_site.register(WPPost, BaseAdmin)
wordpress_import_admin_site.register(WPComment, BaseAdmin)
wordpress_import_admin_site.register(WPMedia, BaseAdmin)
