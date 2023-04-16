import sys

import jmespath
from django.apps import apps

from wagtail_toolbox.wordpress.api_client import Client
from wagtail_toolbox.wordpress.block_builder import WagtailBlockBuilder


class Importer:
    def __init__(self, url, model_name):
        self.client = Client(url)
        self.model = apps.get_model("wordpress", model_name)
        self.fk_objects = []
        self.mtm_objects = []
        self.cleaned_objects = []
        self.import_fields = self.model.include_fields_initial_import(self.model)

    def import_data(self):
        """Import data from wordpress api for each endpoint"""

        sys.stdout.write("Importing data...\n")

        for endpoint in self.client.paged_endpoints:
            sys.stdout.write(f"Importing {self.model.__name__} {endpoint}...\n")
            json_response = self.client.get(endpoint)

            for item in json_response:
                # Some wordpress records have duplicate, essentially unique fields
                # e.g. Tags has name and slug field but names can be the same
                # That doesn't work well with taggit default model, but why would you have 2 the same anyway?
                if hasattr(self.model, "UNIQUE_FIELDS"):
                    qs = self.model.objects.filter(
                        **{field: item[field] for field in self.model.UNIQUE_FIELDS}
                    )
                    if qs.exists():
                        continue  # bail out of this loop,
                        # TODO: the side effect is the object won't be updated only created

                # rename the id field to wp_id
                item["wp_id"] = item.pop("id")
                data = {
                    field: item[field] for field in self.import_fields if field in item
                }

                # some data is nested in the json response
                # so use jmespath to get to it and update the value
                if hasattr(self.model, "process_fields"):
                    for field in self.model.process_fields():
                        for key, value in field.items():
                            data.update({key: jmespath.search(value, item)})

                # create or update the model with data we have so far
                obj, created = self.model.objects.update_or_create(
                    wp_id=item["wp_id"], defaults=data
                )

                sys.stdout.write(f"Created {obj}\n" if created else f"Updated {obj}\n")

                # cache each object for later processing
                self.fk_objects.append(obj)

                # foreign keys
                foreign_key_data = self.get_foreign_key_data(
                    self.model.process_foreign_keys, self.model, item
                )

                obj.wp_foreign_keys = foreign_key_data

                # cache each object for later processing
                self.mtm_objects.append(obj)

                # Process many to many keys
                many_to_many_data = self.get_many_to_many_data(
                    self.model.process_many_to_many_keys, item
                )

                obj.wp_many_to_many_keys = many_to_many_data

                # process clean fields (html)
                self.process_clean_fields(
                    self.model.process_clean_fields,
                    self.model.clean_content_html,
                    self.cleaned_objects,
                    data,
                    obj,
                )

        # process foreign keys here so we have access to all possible
        # foreign keys if the foreign key is self referencing
        # for none self referencing foreign keys the order of imports matters
        self.process_fk_objects(self.fk_objects)
        self.process_mtm_objects(self.mtm_objects)

        # process wagtail blocks
        self.process_wagtail_block_content(
            self.model.process_block_fields(), self.cleaned_objects
        )

    @staticmethod
    def get_many_to_many_data(process_many_to_many_keys, item):
        many_to_many_data = []

        for field in process_many_to_many_keys():
            # each field to process
            for key, value in field.items():
                if item[key]:  # some are empty lists so ignore them
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
                                "value": item[key],
                            },
                        }
                    )

        return many_to_many_data

    @staticmethod
    def get_foreign_key_data(process_foreign_keys, current_model, item):
        foreign_key_data = []

        for field in process_foreign_keys():
            # get each field to process
            for key, value in field.items():
                if item[key]:  # some are just 0 so ignore them
                    """e.g.
                    INPUT:     "parent": {"model": "self", "field": "wp_id"},
                    TRANSFORM: [key] = {[value] = {model: "self", field: "wp_id"}}
                    OUTPUT:    {"parent": {"model": "WPCategory", "where": "wp_id", "value": 38}}
                    """
                    # self = a foreign key to the current model
                    # or it's a foreign key to another model
                    model = (
                        current_model
                        if value["model"] == "self"
                        else apps.get_model("wordpress", value["model"])
                    )

                    foreign_key_data.append(
                        {
                            key: {
                                "model": model.__name__,
                                "where": value["field"],
                                "value": item[key],
                            },
                        }
                    )

        return foreign_key_data

    @staticmethod
    def process_clean_fields(
        clean_fields, clean_content_html, cleaned_objects, data, obj
    ):
        for cleaned_field in clean_fields():
            for source_field, destination_field in cleaned_field.items():
                setattr(
                    obj,
                    destination_field,
                    clean_content_html(data[source_field]),
                )

            cleaned_objects.append(obj)
            obj.save()

    @staticmethod
    def process_fk_objects(fk_objects):
        sys.stdout.write("Processing foreign keys...\n")
        for obj in fk_objects:
            for relation in obj.wp_foreign_keys:
                for field, value in relation.items():
                    try:
                        model = apps.get_model("wordpress", value["model"])
                        where = value["where"]
                        value = value["value"]
                        setattr(obj, field, model.objects.get(**{where: value}))
                    except model.DoesNotExist:
                        sys.stdout.write(
                            f"""Could not find {model.__name__} with {where}={value}. {obj} with id={obj.id}\n"""
                        )
                obj.save()

    @staticmethod
    def process_mtm_objects(mtm_objects):
        sys.stdout.write("Processing many to many keys...\n")
        for obj in mtm_objects:
            for relation in obj.wp_many_to_many_keys:
                related_objects = []
                for field, value in relation.items():
                    model = apps.get_model("wordpress", value["model"])
                    filter = f"""{value["where"]}__in"""
                    related_objects = model.objects.filter(**{filter: value["value"]})
                    if len(related_objects) != len(value["value"]):
                        sys.stdout.write(
                            f"""Some {model.__name__} objects could not be found. {obj} with id={obj.id}\n"""
                        )

                for related_object in related_objects:
                    getattr(obj, field).add(related_object)

    @staticmethod
    def process_wagtail_block_content(block_fields, cleaned_objects):
        sys.stdout.write("Processing Wagtail block content...\n")

        for obj in cleaned_objects:
            # get the configured fields to process
            for operation in block_fields:
                fields = ()
                for k, v in operation.items():
                    fields = (k, v)

                source_data = getattr(obj, fields[0])
                # print(source_data)
                block_data = WagtailBlockBuilder().build(source_data)
                # print(block_data)
                setattr(obj, fields[1], block_data)
                obj.save()
