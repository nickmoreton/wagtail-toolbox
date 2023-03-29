import sys

import jmespath
from django.apps import apps

from wagtail_toolbox.wordpress.api_client import Client
from wagtail_toolbox.wordpress.block_builder import WagtailBlockBuilder


class Importer:
    def __init__(self, host, url, model_name):
        self.client = Client(host, url)
        self.model = apps.get_model("wordpress", model_name)
        self.fk_objects = []
        self.mtm_objects = []
        self.cleaned_objects = []

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

            for item in json_response:
                # Some wordpress records have duplicate essentially unique fields
                # e.g. Tags has name and slug field but names can be the same
                # That doesn't work well with taggit default model, but why would you have 2 the same anyway?
                if hasattr(self.model, "UNIQUE_FIELDS"):
                    qs = self.model.objects.filter(
                        **{field: item[field] for field in self.model.UNIQUE_FIELDS}
                    )
                    if qs.exists():
                        continue  # bail out of this loop

                # item = Item(record)
                item["wp_id"] = item.pop("id")
                data = {field: item[field] for field in import_fields if field in item}

                # some data is nested in the json response
                # so use jmespath to get to it and update the value
                if hasattr(self.model, "process_fields"):
                    for field in self.model.process_fields():
                        for key, value in field.items():
                            data.update({key: jmespath.search(value, item)})

                # TODO: can a way be found to be more specific here
                # so we don't just update everything
                obj, created = self.model.objects.update_or_create(
                    wp_id=item["wp_id"], defaults=data
                )

                sys.stdout.write(f"Created {obj}\n" if created else f"Updated {obj}\n")

                # Process foreign keys, but it is dependent on the foreign key
                # model being imported first
                # for now the data is saved to the model JSONField
                foreign_key_data = []

                for field in self.model.process_foreign_keys():
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
                                self.model
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

                self.fk_objects.append(obj)  # remember for later processing

                # Process many to many keys, but it is dependent on the many to many key
                # model being imported first
                # for now the data is saved to the model JSONField
                many_to_many_data = []

                for field in self.model.process_many_to_many_keys():
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

                self.mtm_objects.append(obj)

                obj.wp_foreign_keys = foreign_key_data
                obj.wp_many_to_many_keys = many_to_many_data

                # cleaned_object_data = []  # for processing in the builder

                # process clean fields (html)
                for cleaned_field in self.model.process_clean_fields():
                    for source_field, destination_field in cleaned_field.items():
                        setattr(
                            obj,
                            destination_field,
                            self.model.clean_content_html(data[source_field]),
                        )

                    self.cleaned_objects.append(obj)
                    obj.save()

        # process foreign keys here so we have access to all possible
        # foreign keys if the foreign key is self referencing
        # for none self referencing foreign keys the order of imports matters
        self.process_fk_objects()
        self.process_mtm_objects()
        self.process_wagtail_block_content(self.cleaned_objects, self.model)

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
                        sys.stdout.write(
                            f"""Could not find {model.__name__} with {where}={value}. {obj} with id={obj.id}\n"""
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
                        sys.stdout.write(
                            f"""Some {model.__name__} objects could not be found. {obj} with id={obj.id}\n"""
                        )

                for related_object in related_objects:
                    getattr(obj, field).add(related_object)

    def process_wagtail_block_content(self, cleaned_objects, model):
        sys.stdout.write("Processing Wagtail block content...\n")

        for obj in cleaned_objects:
            # get the configured fields to process
            for operation in self.model.process_block_fields():
                fields = ()
                for k, v in operation.items():
                    fields = (k, v)

                source_data = getattr(obj, fields[0])
                block_data = WagtailBlockBuilder().build(source_data)
                # print(block_data)
                setattr(obj, fields[1], block_data)
                obj.save()
