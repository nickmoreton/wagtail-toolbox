from django.conf import settings
from django.contrib import admin, messages
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
from wagtail_toolbox.wordpress.utils import check_transfer_available, get_target_mapping


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(settings, "WPI_TRUNCATE_LENGTH"):
            self.truncated_length = 12
        else:
            self.truncated_length = settings.WPI_TRUNCATE_LENGTH

        # does this model have a mapping to a wagtail page in the settings?
        if get_target_mapping(self.model.SOURCE_URL) and check_transfer_available():
            self.actions = [
                "transfer_data_action",
            ]

        # list display field manipulation
        first_fields = [  # these fields will be displayed first
            "name",
            "title",
            "author_name",
        ]
        last_fields = [  # these fields will be displayed last
            "wp_id",
            "wp_foreign_keys",
            "wp_many_to_many_keys",
        ]

        truncated_fields = [  # these fields will have content truncated
            "title",
            "name",
            "content",
            "excerpt",
            "description",
            "caption",
        ]

        remove_fields = [  # these fields will be removed from the list_display
            "wp_foreign_keys",
            "wp_many_to_many_keys",
            "author_avatar_urls",
            "avatar_urls",
        ]

        link_fields = [  # these fields will be displayed as a link to the original wordpress content
            "guid",
            "link",
            "source_url",
        ]

        self.list_display = self.get_list_display_fields(
            self.model,
            remove_fields,
            first_fields,
            last_fields,
            truncated_fields,
            link_fields,
        )

        self.search_fields = [  # these fields will be searchable
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

    def transfer_data_action(self, request, queryset):
        """
        Trigger the transfer of data from wordpress to wagtail models
        on the wordpress model for the selected items in the queryset.
        """
        model = queryset.model
        result = model.transfer_data(model, queryset)

        if result:
            self.message_user(
                request,
                f"""{result['model']} transferred successfully.
                Created: {result['created']} Updated: {result['updated']}""",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "Data transfer failed",
                messages.ERROR,
            )


wordpress_import_admin_site.register(WPPage, BaseAdmin)
wordpress_import_admin_site.register(WPCategory, BaseAdmin)
wordpress_import_admin_site.register(WPTag, BaseAdmin)
wordpress_import_admin_site.register(WPAuthor, BaseAdmin)
wordpress_import_admin_site.register(WPPost, BaseAdmin)
wordpress_import_admin_site.register(WPComment, BaseAdmin)
wordpress_import_admin_site.register(WPMedia, BaseAdmin)
