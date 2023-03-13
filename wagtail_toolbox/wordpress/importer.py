import logging
import sys
from dataclasses import dataclass

import jmespath
from django.apps import apps

from wagtail_toolbox.wordpress.client import Client


@dataclass
class Item:
    # TODO: the original plan was to use this to convert the item id to wp_id and some other things too.
    data: dict

    def __post_init__(self):
        """Convert the item id to wp_id and set it's value."""
        self.data["wp_id"] = self.data.pop("id")


class Importer:
    def __init__(self, host, url, model_name):
        self.client = Client(host, url)
        self.model = apps.get_model("wordpress", model_name)
        self.fk_objects = []
        self.mtm_objects = []

    def import_data(self):
        """From a list of url endpoints fetch the data."""

        sys.stdout.write("Importing data...\n")

        # exclude fields by field name
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

                # some data is nested in the json response
                # so use jmespath to get to it and update the value
                if hasattr(self.model, "process_fields"):
                    for field in self.model.process_fields():
                        for key, value in field.items():
                            data.update({key: jmespath.search(value, item.data)})

                # TODO: can a way be found to be more specific here
                # so we don't just update everything
                obj, created = self.model.objects.update_or_create(
                    wp_id=item.data["wp_id"], defaults=data
                )

                sys.stdout.write(f"Created {obj}\n" if created else f"Updated {obj}\n")

                # Process foreign keys, but it is dependent on the foreign key
                # model being imported first
                # for now the data is saved to the model JSONField
                foreign_key_data = []

                for field in self.model.process_foreign_keys():
                    # get each field to process
                    for key, value in field.items():
                        if item.data[key]:  # some are just 0 so ignore them
                            """e.g.
                            INPUT:     "parent": {"model": "self", "field": "wp_id"},
                            TRANSFORM: [key] = {[value] = {model: "self", field: "wp_id"}}
                            OUTPUT:    {"parent": {"model": "WPCategory", "where": "wp_id", "value": 38}}
                            """
                            # self = a foreign key to the current model
                            # or it's a foreign key to another model
                            model = (
                                self.model
                                if value["model"] == "self"
                                else apps.get_model("wordpress", value["model"])
                            )

                            foreign_key_data.append(
                                {
                                    key: {
                                        "model": model.__name__,
                                        "where": value["field"],
                                        "value": item.data[key],
                                    },
                                }
                            )

                self.fk_objects.append(obj)  # remember for later processing

                # Process many to many keys, but it is dependent on the many to many key
                # model being imported first
                # for now the data is saved to the model JSONField
                many_to_many_data = []

                for field in self.model.process_many_to_many_keys():
                    # each field to process
                    for key, value in field.items():
                        if item.data[key]:  # some are empty lists so ignore them
                            """
                            TRANSFORM: [key] = {[value] = {model: "WPCategory", field: "wp_id"}}
                            OUTPUT:    [{"categories": {"model": "WPCategory", "where": "wp_id", "value": 38}}]
                            """

                            # assuming all many to many keys are to other models
                            model = apps.get_model("wordpress", value["model"])

                            # values = item.data[key]
                            many_to_many_data.append(
                                {
                                    key: {
                                        "model": model.__name__,
                                        "where": value["field"],
                                        "value": item.data[key],
                                    },
                                }
                            )

                self.mtm_objects.append(obj)

                obj.wp_foreign_keys = foreign_key_data
                obj.wp_many_to_many_keys = many_to_many_data

                obj.save()

        # process foreign keys here so we have access to all possible
        # foreign keys if the foreign key is self referencing
        # for none self referencing foreign keys the order of imports matters
        self.process_fk_objects()
        self.process_mtm_objects()

    def process_fk_objects(self):
        sys.stdout.write("Processing foreign keys...\n")
        for obj in self.fk_objects:
            for relation in obj.wp_foreign_keys:
                for field, value in relation.items():
                    try:
                        model = apps.get_model("wordpress", value["model"])
                        where = value["where"]
                        value = value["value"]
                        setattr(obj, field, model.objects.get(**{where: value}))
                    except model.DoesNotExist:
                        logging.warning(
                            f"""Could not find {model} with {where}={value}.
                            This was called from {obj} with id={obj.id}"""
                        )
                obj.save()

    def process_mtm_objects(self):
        sys.stdout.write("Processing many to many keys...\n")
        for obj in self.mtm_objects:
            for relation in obj.wp_many_to_many_keys:
                related_objects = []
                for field, value in relation.items():
                    model = apps.get_model("wordpress", value["model"])
                    filter = f"""{value["where"]}__in"""
                    related_objects = model.objects.filter(**{filter: value["value"]})
                    if len(related_objects) != len(value["value"]):
                        logging.warning(
                            f"Some {model} objects could not be found. This was called from {obj} with id={obj.id}"
                        )

                for related_object in related_objects:
                    getattr(obj, field).add(related_object)
