import sys
from dataclasses import dataclass

import requests
from django.apps import apps


class Importer:
    def __init__(self, host, url, model_name):
        self.client = Client(host, url)
        self.model = apps.get_model("wordpress", model_name)
        self.process_fk_objects = []

    def import_data(self):
        """From a list of url endpoints fetch the data."""

        sys.stdout.write("Importing data...\n")

        exclude_fields = self.model.exclude_fields_initial_import(self.model)

        import_fields = [
            f.name
            for f in self.model._meta.get_fields()
            if f.name != "id" and f.name not in exclude_fields
        ]

        for endpoint in self.client.paged_endpoints:
            json_response = self.client.get(endpoint)

            for record in json_response:
                item = Item(record)
                data = {
                    field: item.data[field]
                    for field in import_fields
                    if field in item.data
                }

                obj, created = self.model.objects.update_or_create(
                    wp_id=item.data["wp_id"], defaults=data
                )

                sys.stdout.write(f"Created {obj}\n" if created else f"Updated {obj}\n")

                if hasattr(self.model, "process_foreign_keys"):
                    for field in self.model.process_foreign_keys():
                        # create a dict of the foreign key fields and values
                        # that will be saved to wp_foreign_keys
                        if item.data["parent"]:  # some are just 0 so ignore them
                            self.process_fk_objects.append(obj)
                            for key, value in field.items():
                                if value["model"] == "self":
                                    model = self.model
                                else:
                                    model = apps.get_model("wordpress", key["model"])

                                save_data = {
                                    key: {
                                        "model": model.__name__,
                                        "where": value["field"],
                                        "value": item.data["wp_id"],
                                    },
                                }
                                obj.wp_foreign_keys = save_data
                                obj.save()

        if self.process_fk_objects:
            print("Processing foreign keys...")
            for obj in self.process_fk_objects:
                for field in obj.wp_foreign_keys:
                    model = apps.get_model(
                        "wordpress", obj.wp_foreign_keys[field]["model"]
                    )
                    where = obj.wp_foreign_keys[field]["where"]
                    value = obj.wp_foreign_keys[field]["value"]
                    setattr(obj, field, model.objects.get(**{where: value}))
                obj.save()
                print(f"Processed foreign keys for {obj}")


@dataclass
class Item:
    data: dict

    def __post_init__(self):
        """Convert the item id to wp_id and set it's value."""
        self.data["wp_id"] = self.data.pop("id")


_session = requests.Session()


class Client:
    def __init__(self, host, url):
        self.host = host
        self.url = url

        try:
            self.response = _session.get(self.build_url)

            sys.stdout.write(f"Fetching {self.build_url}\n")

            if not self.response.ok:
                sys.stdout.write(f"Error: {self.response.text}\n")
                raise Exception(self.response.text)
        except Exception as e:
            sys.stdout.write(f"Error: {e}\n")
            raise e

    def get(self, url):
        try:
            return _session.get(url).json()
        except Exception as e:
            raise e

    @property
    def build_url(self):
        return f"{self.host}/{self.url}"

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
