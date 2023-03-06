from wagtail.contrib.modeladmin.options import modeladmin_register

from wagtail_toolbox.wordpress.wagtail_hooks import TagsModelAdmin

modeladmin_register(TagsModelAdmin)
