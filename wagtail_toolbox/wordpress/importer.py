import sys
from dataclasses import dataclass

import jmespath
import requests
from django.apps import apps


class Importer:
    def __init__(self, host, url, model_name):
        self.client = Client(host, url)
        self.model = apps.get_model("wordpress", model_name)
        self.process_fk_objects = []
        self.process_many_to_many_objects = []

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

                if hasattr(self.model, "process_fields"):
                    for field in self.model.process_fields():
                        for key, value in field.items():
                            # print(jmespath.search(value, item.data))
                            data[key] = jmespath.search(value, item.data)

                obj, created = self.model.objects.update_or_create(
                    wp_id=item.data["wp_id"], defaults=data
                )

                sys.stdout.write(f"Created {obj}\n" if created else f"Updated {obj}\n")

                if hasattr(self.model, "process_foreign_keys"):
                    save_data = []
                    for field in self.model.process_foreign_keys():
                        # each field to process
                        for key, value in field.items():
                            """
                            INPUT:     "parent": {"model": "self", "field": "wp_id"},
                            TRANSFORM: [key] = {[value] = {model: "self", field: "wp_id"}}
                            OUTPUT:    {"parent": {"model": "WPCategory", "where": "wp_id", "value": 38}}
                            """
                            if value["model"] == "self":
                                # self is a reference to the current model
                                model = self.model
                            else:
                                # or a reference to another model
                                model = apps.get_model("wordpress", value["model"])

                            if item.data[key]:
                                # some are just 0 so ignore them
                                save_data.append(
                                    {
                                        key: {
                                            "model": model.__name__,
                                            "where": value["field"],
                                            "value": item.data[key],
                                        },
                                    }
                                )

                    obj.wp_foreign_keys = save_data  # the output
                    obj.save()
                    self.process_fk_objects.append(obj)  # remember for later processing

                if hasattr(self.model, "process_many_to_many_keys"):
                    save_data = []
                    for field in self.model.process_many_to_many_keys():
                        # each field to process
                        # INPUT: "categories": {"model": "WPCategory", "field": "wp_id"},
                        # can be multiple related models
                        for key, value in field.items():
                            """
                            TRANSFORM: [key] = {[value] = {model: "WPCategory", field: "wp_id"}}
                            OUTPUT:    [{"categories": {"model": "WPCategory", "where": "wp_id", "value": 38}}]
                            """
                            # if value["model"] == "self":
                            #     # self is a reference to the current model
                            #     model = self.model
                            # else:
                            #     # or a reference to another model
                            model = apps.get_model("wordpress", value["model"])

                            if item.data[key]:
                                # some are empty lists so ignore them
                                # save_data = []
                                values = item.data[key]
                                # print(item.data[key])
                                # for value in item.data[key]:
                                # print(values)
                                save_data.append(
                                    {
                                        key: {
                                            "model": model.__name__,
                                            "where": value["field"],
                                            "value": values,
                                        },
                                    }
                                )

                    obj.wp_many_to_many_keys = save_data
                    obj.save()
                    self.process_many_to_many_objects.append(obj)

        # process foreign keys here so we have access to all possible
        # foreign keys if the foreign key is self referencing
        # for none self referencing foreign keys the order of imports matters
        if self.process_fk_objects:
            print("Processing foreign keys...")
            for obj in self.process_fk_objects:
                for relation in obj.wp_foreign_keys:
                    for field, value in relation.items():
                        model = apps.get_model("wordpress", value["model"])
                        where = value["where"]
                        value = value["value"]
                        setattr(obj, field, model.objects.get(**{where: value}))
                obj.save()
            #         model = apps.get_model(
            #             "wordpress", obj.wp_foreign_keys[field]["model"]
            #         )
            #         where = obj.wp_foreign_keys[field]["where"]
            #         value = obj.wp_foreign_keys[field]["value"]
            #         setattr(obj, field, model.objects.get(**{where: value}))
            #     obj.save()
            #     print(f"Processed foreign keys for {obj}")

        if self.process_many_to_many_objects:
            print("Processing many to many keys...")
            for obj in self.process_many_to_many_objects:
                # print(obj.wp_many_to_many_keys)
                for relation in obj.wp_many_to_many_keys:
                    related_objects = []
                    for field, value in relation.items():
                        model = apps.get_model("wordpress", value["model"])
                        filter = f"""{value["where"]}__in"""
                        # where = value["where"]
                        # values = value["value"]
                        # related_objects = model.objects.filter({where: values})
                        related_objects = model.objects.filter(
                            **{filter: value["value"]}
                        )
                        # set the related objects on the object
                        for related_object in related_objects:
                            getattr(obj, field).add(related_object)
                        # obj.__dict__[field] = related_objects
                        # obj.save()
                    # obj[field] = related_objects

                    # obj[field].set(related_objects)
                    # print(model, where, values)
                    # for v in values:
                    #     setattr(obj, field, model.objects.get(**{where: v}))
                # obj.save()
            #     for field in obj.wp_foreign_keys:
            #         model = apps.get_model(
            #             "wordpress", obj.wp_foreign_keys[field]["model"]
            #         )
            #         where = obj.wp_foreign_keys[field]["where"]
            #         value = obj.wp_foreign_keys[field]["value"]
            #         setattr(obj, field, model.objects.get(**{where: value}))
            #     obj.save()
            #     print(f"Processed many to many keys for {obj}")


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
