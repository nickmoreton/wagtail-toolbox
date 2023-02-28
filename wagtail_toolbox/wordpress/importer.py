import logging
from dataclasses import dataclass

import requests
from django.apps import apps


class Importer:
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    def __init__(self, host, url, endpoint, model_name):
        self.client = Client(host, url, endpoint)
        self.model = self.get_model_class(model_name)

    def import_data(self):
        """From a list of url endpoints fetch the data.

        Each page has any number of records so we need to loop through
        them and create an item for each record.

        The item is returned with pre-processing done."""

        exclude_fields = self.exclude_fields(self.model)

        fields = self.get_object_fields(self.model, exclude_fields=exclude_fields)

        for endpoint in self.client.paged_endpoints:
            json_response = self.client.get(endpoint)

            for record in json_response:
                item = Item(record)
                data = {x: item.data[x] for x in fields if x in item.data}

                obj, created = self.model.objects.update_or_create(
                    wp_id=item.data["wp_id"], defaults=data
                )

                logging.debug(f"Created {obj}") if created else logging.debug(
                    f"Updated {obj}"
                )

    @staticmethod
    def get_model_class(model_class):
        return apps.get_model("wordpress", model_class)

    @staticmethod
    def exclude_fields(model):
        """Return a list of fields to exclude from the model initial import."""
        return [x for x in model.relationships_foreign_keys().keys()]

    def get_object_fields(self, model, exclude_fields=None):
        # related fields are not included
        # because they are processed later
        fields = [
            f.name
            for f in model._meta.get_fields()
            if f.name != "id" and f.name not in exclude_fields
        ]
        return fields


@dataclass
class Item:
    data: dict

    def __post_init__(self):
        """Convert the item id to wp_id and set it's value."""
        self.data["wp_id"] = self.data.pop("id")


_session = requests.Session()


class Client:
    def __init__(self, host, url, endpoint):
        self.host = host
        self.url = url
        self.endpoint = endpoint
        try:
            self.response = _session.get(self.build_url)
            if not self.response.ok:
                raise Exception(self.response.text)
        except Exception as e:
            raise e

    def get(self, url):
        try:
            return _session.get(url).json()
        except Exception as e:
            raise e

    @property
    def build_url(self):
        return f"{self.host}/{self.url}/{self.endpoint}"

    @property
    def is_paged(self):
        """Return True if the endpoint is paged, False otherwise."""

        return "X-WP-TotalPages" in self.response.headers

    @property
    def get_total_pages(self):
        """Return the total number of pages."""

        if self.is_paged:
            return int(self.response.headers["X-WP-TotalPages"])

        return 1

    @property
    def get_total_results(self):
        """Return the total number of results."""

        if "X-WP-Total" in self.response.headers:
            return int(self.response.headers["X-WP-Total"])

    @property
    def paged_endpoints(self):
        """Generate a list of URLs that can be fetched.
        The 'page' parameter is always appended to the URL.
        Returns:
            A list of URLs.
        Example:
            [
                "https://foo.com/endpoint/bar/baz?page=1",
                "https://foo.com/endpoint/bar/baz?page=2",
            ]
        """

        total_pages = self.get_total_pages

        return [f"{self.build_url}?page={index}" for index in range(1, total_pages + 1)]
