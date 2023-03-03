# from django import forms
# from wagtail.admin.panels import FieldPanel
# from wagtail.models import Site

# from wagtail_toolbox.wordpress.utils import wordpress_routes

# site = Site.objects.get(is_default_site=True)
# wordpress_settings = site.settings.wordpress_settings


# class EndpointSelectWidget(forms.Select):
#     def __init__(self, attrs=None, choices=()):
#         super().__init__(attrs, choices)
#         self.attrs["onchange"] = "set_endpoint_url_model(this)"

#     class Media:
#         js = ("wordpress/js/endpoint_select.js",)


# class EndpointSelectPanel(FieldPanel):
#     def __init__(self, field_name, **kwargs):
#         super().__init__(field_name, **kwargs)
#         choices = (("", "---------"),)
#         for route in wordpress_routes():
#             for _, value in route.items():
#                 choices += ((value["name"], value["name"]),)

#         self.widget = EndpointSelectWidget(choices=choices)
