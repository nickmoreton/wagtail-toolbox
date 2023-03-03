import requests
from django import forms
from wagtail.admin.panels import FieldPanel


def wordpress_routes():
    resp = requests.get("https://wordpress.nickmoreton.co.uk/wp-json/")
    if resp.status_code != 200:
        raise Exception("Could not get wordpress routes")
    routes = [
        {
            "wp-json"
            + route: {
                "host": value.get("_links")["self"][0]["href"],
                "name": route.split("/")[-1],
                "model": "WP" + route.split("/")[-1].capitalize(),
            }
        }
        for route, value in resp.json()["routes"].items()
        if value["namespace"] == "wp/v2"
        and (value["methods"] == ["GET", "POST"] or value["methods"] == ["GET"])
        and len(route.split("/")) == 4  # only get the top level routes
    ]
    sorted_routes = sorted(routes, key=lambda x: list(x.keys())[0])
    return sorted_routes


class EndpointSelectWidget(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
        self.attrs["onchange"] = "set_endpoint_url_model(this)"

    class Media:
        js = ("wordpress/js/endpoint_select.js",)


class EndpointSelectPanel(FieldPanel):
    def __init__(self, field_name, **kwargs):
        super().__init__(field_name, **kwargs)
        choices = (("", "---------"),)
        for route in wordpress_routes():
            for _, value in route.items():
                choices += ((value["name"], value["name"]),)

        self.widget = EndpointSelectWidget(choices=choices)
