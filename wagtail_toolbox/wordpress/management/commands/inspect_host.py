import json

import requests
from django.conf import settings
from django.core.management import BaseCommand

from wagtail_toolbox.wordpress.models import WordpressEndpoint, WordpressHost

# from wagtail_toolbox.wordpress.wordpress_import import Importer

# from wagtail_toolbox.wordpress.inspector import Inspector
# from wagtail_toolbox.wordpress.utils import parse_wordpress_routes


class Command(BaseCommand):
    help = "Import WordPress data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            help="The WordPress host domain name.",
            default="",
        )
        parser.add_argument(
            "--path",
            type=str,
            help="The path to the WordPress site json API.",
            default="",
        )
        parser.add_argument(
            "--exclude",
            type=str,
            help="Comma separated list of endpoints to exclude.",
            default="",  # "WPPage,WPPost"
        )
        parser.add_argument(
            "--save",
            action="store_true",
            help="Save the routes to the settings database.",
            default=False,
        )

    def handle(self, *args, **options):
        if (
            not hasattr(settings, "WPI_DOMAIN")
            or not settings.WPI_DOMAIN
            and not options["domain"]
        ):
            self.stderr.write("WPI_DOMAIN is not defined in your settings.")
            self.stdout.write(
                "Please define it and try again or use the --domain option."
            )
            return

        domain = options["domain"] if options["domain"] else settings.WPI_DOMAIN

        path = (
            options["path"]
            if options["path"]
            else settings.WPI_PATH
            if hasattr(settings, "WPI_PATH")
            else "wp-json/wp/v2"
        )
        exclude = (
            options["exclude"].split(",")
            if options["exclude"]
            else settings.WPI_EXCLUDE_ENDPOINTS
            if hasattr(settings, "WPI_EXCLUDE_ENDPOINTS")
            else []
        )

        url = f"{domain}/{path}"
        routes = self.parse_wordpress_routes(url, exclude)

        self.stdout.write(json.dumps(routes, indent=1))

        if options["save"]:
            self.save_routes(routes)

    def parse_wordpress_routes(self, url, exclude):
        try:
            resp = requests.get(url, timeout=3)
        except requests.exceptions.ConnectionError:
            self.stderr.write("Could not connect to wordpress host")
            return []

        if resp.status_code != 200:
            raise Exception("Could not get wordpress routes")
        routes = [
            {
                "url": value.get("_links")["self"][0]["href"],
                "name": route.split("/")[-1],
                "model": "WP" + route.split("/")[-1].capitalize(),
            }
            for route, value in resp.json()["routes"].items()
            if value["namespace"] == "wp/v2"
            and (value["methods"] == ["GET", "POST"] or value["methods"] == ["GET"])
            and len(route.split("/")) == 4  # only get the top level routes
        ]

        if exclude:
            trimmed_routes = []
            for route in routes:
                if route["name"] not in exclude:
                    trimmed_routes.append(route)
            routes = trimmed_routes

        return sorted(routes, key=lambda x: list(x.keys())[0])

    def save_routes(self, routes):
        host_settings = WordpressHost.objects.all().first()
        host_endpoints = host_settings.wordpress_endpoints.all()

        for route in routes:
            if not host_endpoints.filter(name=route["name"]).exists():
                endpoint = WordpressEndpoint(
                    name=route["name"],
                    url=route["url"],
                    model=route["model"],
                    setting=host_settings,
                )
                endpoint.save()
                host_settings.wordpress_endpoints.add(endpoint)
                host_settings.save()
            else:
                endpoint = host_endpoints.get(name=route["name"])
                endpoint.url = route["url"]
                endpoint.model = route["model"]
                endpoint.save()
