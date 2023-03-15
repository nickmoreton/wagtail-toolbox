from django.apps import apps
from django.conf import settings


class Transferrer:
    """
    Transfers data from a wordpress model to a wagtail model.

    :param host: The wordpress host.
    :param url: The wordpress api url.
    :param wordpress_source: The wordpress model to transfer.
    :param wagtail_target: The wagtail model to transfer to.
    :param wordpress_primary_keys: The primary keys of the wordpress models to transfer.

    :type host: str
    :type url: str
    :type wordpress_source: str
    :type wagtail_target: str
    :type wordpress_primary_keys: str

    :returns: None
    """

    def __init__(
        self,
        wordpress_source,
        wagtail_target,
        wordpress_primary_keys,
        dry_run=False,
        include_related=True,
        parent_page=None,
    ):
        self.dry_run = dry_run
        self.include_related = include_related
        self.pks = wordpress_primary_keys.split(",")
        self.parent_page = parent_page
        self.source = wordpress_source
        self.target = wagtail_target

        self.results = {}

    def get_target_model(self):
        """Get the target model."""
        try:
            return apps.get_model(self.target)
        except LookupError:
            raise LookupError(f"Could not find target model {self.target}")

    def get_source_model(self):
        """Get the source model."""
        try:
            return apps.get_model(self.source)
        except LookupError:
            raise LookupError(f"Could not find source model {self.source}")

    def get_source_queryset(self):
        """Get the source queryset."""
        source_model = self.get_source_model()
        return source_model.objects.filter(pk__in=self.pks)

    @property
    def get_model_type(self):
        """Get the model type of the target model."""
        fields_mapping = settings.WPI_TARGET_MAPPING.get(self.target, None)
        if not fields_mapping:
            raise Exception(f"No mapping found for {self.target}")

        if "model_type" in fields_mapping:
            return fields_mapping["model_type"]

    @property
    def get_target_fields(self):
        """Get the fields of the source model from the config."""

        fields_mapping = settings.WPI_TARGET_MAPPING.get(self.target, None)

        if not fields_mapping:
            raise Exception(f"No mapping found for {self.target}")

        return fields_mapping["fields"]

        # deferrable fields are fields that represent a relationship
        # so we don't want to transfer them in the initial transfer
        # because some are self referential and will cause an error
        # related_mapping = fields_mapping.get("related_mapping", [])
        # many_to_many_mapping = fields_mapping.get("many_to_many_mapping", [])

        # deferrable_fields = []

        # for field in related_mapping["fields"]:
        #     deferrable_fields.append(field)
        # for field in many_to_many_mapping["fields"]:
        #     deferrable_fields.append(field)

        # return [field for field in fields if field not in deferrable_fields]
        # return fields

    def transfer(self):
        if not self.get_source_queryset():
            return False

        return self.transfer_data(
            self.get_source_queryset(),
            self.get_target_model(),
            self.get_model_type,
        )

    def transfer_data(self, queryset, target_model, model_type=None):
        """Transfer data from the source model to the target model."""

        target_fields = self.get_target_fields

        for item in queryset:
            values = {field: getattr(item, field) for field in target_fields}

            # just in case the title is empty, it's possible in wordpress
            # for some reason, then set the title to `Untitled`
            # seems to be the case for pages
            if (
                hasattr(target_model, "title") and not values["title"]
            ):  # TODO: is this also the case for other fields?
                values["title"] = "Untitled"

            obj = target_model.objects.filter(slug=values["slug"]).first()

            action = "updated" if obj else "created"

            if model_type == "page":
                obj = (
                    self.update_page(values, target_model)
                    if obj
                    else self.save_page(values, target_model)
                )

            elif not model_type:
                if obj:
                    for key, value in values.items():
                        setattr(obj, key, value)
                else:
                    obj = target_model(**values)

                obj.save() if not self.dry_run else None

            item.wagtail_model = {
                "model": self.target,
                "pk": obj.pk,
            }
            item.save() if not self.dry_run else None

            self.results[
                f"{item.pk}-{model_type if model_type else 'object'}"
            ] = f"{obj} ({obj.pk}) {action}"

        # now deal with the deferrable fields aka the relationships
        fields_mapping = settings.WPI_TARGET_MAPPING.get(self.target, None)
        if not fields_mapping:
            raise Exception(f"No mapping found for {self.target}")

        related_mapping = fields_mapping.get("related_mapping", [])
        many_to_many_mapping = fields_mapping.get("many_to_many_mapping", [])
        cluster_mapping = fields_mapping.get("cluster_mapping", [])

        for related in related_mapping:
            self.transfer_related(related, queryset, target_model, model_type)

        for many_to_many in many_to_many_mapping:
            self.transfer_many_to_many(many_to_many, queryset, target_model, model_type)

        for cluster in cluster_mapping:
            self.transfer_taggable(cluster, queryset, target_model, model_type)

        return self.results

    def transfer_related(
        self, related_mapping, queryset, target_model, model_type=None
    ):
        """Transfer related fields."""
        # "related_mapping": [
        # {
        #     "source_field": "author",  # the related object field on the source model
        #     "source_value": "slug",  # the value to search for update or create
        #     "target_field": "author",  # the field of the target model to map to
        #     "target_model": "blog.BlogAuthor",  # the model for the new object
        #     "model_type": "model",  # the model type (page or model)
        #     "fields": {  # the fields to transfer on create or update
        #         "name": "name",
        #         "slug": "slug",
        #     },
        # },
        for item in queryset:
            related_source_obj = getattr(item, related_mapping["source_field"])
            related_target_model = apps.get_model(related_mapping["target_model"])
            target_object = apps.get_model(item.wagtail_model["model"]).objects.get(
                pk=item.wagtail_model["pk"]
            )

            if related_source_obj:
                if related_mapping["model_type"] == "model":
                    related_obj = related_target_model.objects.filter(
                        **{
                            related_mapping["source_value"]: getattr(
                                related_source_obj, related_mapping["source_value"]
                            )
                        }
                    ).first()
                    if not related_obj:
                        source_values = {
                            field: getattr(related_source_obj, value)
                            for field, value in related_mapping["fields"].items()
                        }
                        related_obj = related_target_model(**source_values)
                        related_obj.save() if not self.dry_run else None
                    else:
                        for field, value in related_mapping["fields"].items():
                            setattr(
                                related_obj, field, getattr(related_source_obj, value)
                            )
                        related_obj.save() if not self.dry_run else None
                    setattr(target_object, related_mapping["target_field"], related_obj)
                    target_object.save() if not self.dry_run else None
                elif related_mapping["model_type"] == "page":
                    pass  # TODO: implement this for WPPages or more

            self.results[f"{item.pk}-related-field"] = f"{item} ({item.pk})"

    def transfer_many_to_many(
        self, many_to_many_mapping, queryset, target_model, model_type=None
    ):
        """Transfer many to many fields."""
        # "many_to_many_mapping": [
        # {
        #     "source_field": "categories",  # the related object field on the source model
        #     "source_value": "slug",  # the value to search for update or create
        #     "target_field": "categories",  # the field of the target model to map to
        #     "target_model": "blog.BlogCategory",  # the model for the new object
        #     "model_type": "model",  # the model type (page or model)
        #     "fields": {  # the fields to transfer on create or update
        #         "name": "name",
        #         "slug": "slug",
        #     },
        # },
        for item in queryset:
            related_source_obj = getattr(item, many_to_many_mapping["source_field"])
            related_target_model = apps.get_model(many_to_many_mapping["target_model"])
            target_object = apps.get_model(item.wagtail_model["model"]).objects.get(
                pk=item.wagtail_model["pk"]
            )

            if related_source_obj:
                source_related_objects = getattr(
                    item, many_to_many_mapping["source_field"]
                ).all()
                if many_to_many_mapping["model_type"] == "model":
                    for related_source_obj in source_related_objects:
                        related_obj = related_target_model.objects.filter(
                            **{
                                many_to_many_mapping["source_value"]: getattr(
                                    related_source_obj,
                                    many_to_many_mapping["source_value"],
                                )
                            }
                        ).first()
                        if not related_obj:
                            source_values = {
                                field: getattr(related_source_obj, value)
                                for field, value in many_to_many_mapping[
                                    "fields"
                                ].items()
                            }
                            related_obj = related_target_model(**source_values)
                            related_obj.save() if not self.dry_run else None
                        else:
                            for field, value in many_to_many_mapping["fields"].items():
                                setattr(
                                    related_obj,
                                    field,
                                    getattr(related_source_obj, value),
                                )
                            related_obj.save() if not self.dry_run else None
                        getattr(
                            target_object, many_to_many_mapping["target_field"]
                        ).add(related_obj)
                        target_object.save() if not self.dry_run else None

                elif many_to_many_mapping["model_type"] == "page":
                    pass
                    # TODO: implement this for WPPages or more

    def transfer_taggable(
        self, cluster_mapping, queryset, target_model, model_type=None
    ):
        """Transfer taggable fields."""

        for item in queryset:
            related_source_obj = getattr(item, cluster_mapping["source_field"])
            related_target_model = apps.get_model(  # noqa
                cluster_mapping["target_model"]
            )  # noqa
            target_object = apps.get_model(item.wagtail_model["model"]).objects.get(
                pk=item.wagtail_model["pk"]
            )

            if related_source_obj:  # if item actually has results
                # remove any existing related objects for the target object
                getattr(target_object, cluster_mapping["target_field"]).clear()

                # get the related objects from the source object
                source_related_objects = getattr(
                    item, cluster_mapping["source_field"]
                ).all()

                # add the related objects to the target object
                setattr(
                    target_object,
                    cluster_mapping["target_field"],
                    source_related_objects,
                )

                if cluster_mapping["model_type"] == "model":
                    target_model.save() if not self.dry_run else None
                elif cluster_mapping["model_type"] == "page":
                    rev = target_model.save_revision() if not self.dry_run else None
                    rev.publish() if not self.dry_run else None

                """
                creates the tags but not linking to the page model
                """

    def save_page(self, values, target_model, parent_page=None):
        """Save a page the way wagtail like it."""

        if not self.parent_page:
            parent_model = apps.get_model(
                settings.WPI_TARGET_BLOG_INDEX[0], settings.WPI_TARGET_BLOG_INDEX[1]
            )
            parent_page = parent_model.objects.first()
            if not parent_page:
                exit("No parent page found.")

        page = target_model(**values)

        if not self.dry_run:
            parent_page.add_child(instance=page)
            page.save_revision().publish()

        return page

    def update_page(self, values, target_model):
        """Update a page the way wagtail like it."""

        page = target_model.objects.filter(slug=values["slug"]).first()

        if not self.dry_run:
            revision = page.save_revision()
            revision.publish()

        return page
