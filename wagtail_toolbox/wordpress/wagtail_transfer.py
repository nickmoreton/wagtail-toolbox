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

        try:
            self.source_model = apps.get_model(self.source)
        except LookupError:
            raise LookupError(f"Could not find model {self.source}")

        try:
            self.target_model = apps.get_model(self.target)
        except LookupError:
            raise LookupError(f"Could not find model {self.target}")

        self.source_queryset = self.source_model.objects.filter(pk__in=self.pks)

        self.results = {}

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
        """Get the fields of the source model."""

        fields_mapping = settings.WPI_TARGET_MAPPING.get(self.target, None)
        if not fields_mapping:
            raise Exception(f"No mapping found for {self.target}")

        fields = fields_mapping["fields"]
        deferrable_fields = (
            fields_mapping["deferrable_fields"]
            if "deferrable_fields" in fields_mapping
            else []
        )

        return [field for field in fields if field not in deferrable_fields]

    def transfer(self):
        if not self.source_queryset:
            return False

        qs = self.source_queryset
        target_model = self.target_model

        results = self.transfer_data(qs, target_model, self.get_model_type)  # noqa

        return self.results

    def transfer_data(self, queryset, target_model, model_type=None):
        """Transfer data from the source model to the target model."""

        target_fields = self.get_target_fields

        for item in queryset:
            values = {field: getattr(item, field) for field in target_fields}

            # just in case the title is empty, it's possible in wordpress
            # for some reason then set the title to `Untitled`
            if (
                hasattr(target_model, "title") and not values["title"]
            ):  # TODO: is this also the case for other fields?
                values["title"] = "Untitled"

            if model_type == "page":
                obj = target_model.objects.filter(slug=values["slug"]).first()
                if obj:
                    obj = self.update_page(values, target_model)
                else:
                    obj = self.save_page(values, target_model)
            else:
                obj = target_model.objects.filter(slug=values["slug"]).first()
                if obj:
                    for key, value in values.items():
                        setattr(obj, key, value)
                    obj.save()
                else:
                    obj = target_model(**values)
                    obj.save()

            self.results[item.pk] = obj.pk

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
        parent_page.add_child(instance=page)
        page.save_revision().publish()

        return page

    def update_page(self, values, target_model):
        """Update a page the way wagtail like it."""

        page = target_model.objects.filter(slug=values["slug"]).first()

        revision = page.save_revision()
        revision.publish()

        return page

        # page =

        # print(target_fields)

        # for obj in queryset:
        #     values = {}
        #     for field in fields:
        #         values[field.name] = getattr(obj, field.name)
        #     # if not self.dry_run:
        #         # target_model.objects.create(**values)
        #     print(values)

        # config = get_target_mapping(model.SOURCE_URL)
        # target_model = get_target_model(config)
        # related_mappings = get_related_mapping(config)
        # many_to_many_mappings = get_many_to_many_mapping(config)
        # model_type = get_model_type(config)

        # field_names = []

        # # exclude fields either not required or will be processed later
        # exclude_internal_fields = [
        #     "ForeignKey",
        #     "ParentalKey",
        #     "OneToOneField",
        #     "ManyToManyField",
        #     "ParentalManyToManyField",
        # ]

        # for field in target_model._meta.get_fields(
        #     include_parents=False, include_hidden=False
        # ):
        #     if field.get_internal_type() not in exclude_internal_fields:
        #         field_names.append(field.name)

        # results = {
        #     "created": 0,
        #     "updated": 0,
        # }

        # related = []
        # many_to_many = []

        # for obj in queryset:  # queryset is a list of objects from the source model
        #     values = {}
        #     for field_name in field_names:
        #         if hasattr(obj, field_name):
        #             values[field_name] = getattr(obj, field_name)

        #     try:  # noticed some errors with slug field having emoji characters in it
        #         if model_type == "page":
        #             page, created = WordpressModel.save_page(obj, target_model, values)
        #         elif model_type == "model":
        #             page, created = target_model.objects.get_or_create(**values)

        #     except Exception as e:
        #         print(f"Error: {e} - {obj.wp_id} - {obj.get_title}")
        #         continue

        #     # pull out related fields
        #     for related_mapping in related_mappings:
        #         # ("author", "author", "blog.BlogAuthor"),
        #         related_field_obj = getattr(obj, related_mapping[0])
        #         if related_field_obj:
        #             related.append(
        #                 {
        #                     "related_obj": related_field_obj,
        #                     "related_field": related_mapping[1],
        #                     "target_obj": page,
        #                     "related_model": related_mapping[2],
        #                 }
        #             )

        #     # pull out many to many fields
        #     for many_to_many_mapping in many_to_many_mappings:
        #         # ("categories", "categories", "blog.BlogCategory"),
        #         source_field_objects = getattr(obj, many_to_many_mapping[0]).all()
        #         for source_field_obj in source_field_objects:
        #             many_to_many.append(
        #                 {
        #                     "model": model,
        #                     "source": source_field_objects,
        #                     "target": page,
        #                     "field": many_to_many_mapping[1],
        #                 }
        #             )

        #     if created:
        #         results["created"] += 1
        #     else:
        #         results["updated"] += 1

        # results["total"] = results["created"] + results["updated"]
        # results["model"] = target_model._meta.verbose_name_plural

        # return results, related, many_to_many

    # def save_page(self, source_obj, tar, values, parent_page=None):
    #     """Save the page the way wagtail likes it."""
    #     if not parent_page:
    #         parent_model = apps.get_model(
    #             settings.WPI_TARGET_BLOG_INDEX[0], settings.WPI_TARGET_BLOG_INDEX[1]
    #         )
    #         parent_page = parent_model.objects.first()

    #     values.update(
    #         {
    #             "title": obj.title if obj.title else "Untitled",
    #             "slug": obj.slug,
    #         }
    #     )

    #     page_obj = parent_page.get_children().filter(slug=obj.slug).first()

    #     if page_obj:
    #         page_obj = page_obj.specific
    #         for key, value in values.items():
    #             setattr(page_obj, key, value)
    #         rev = page_obj.save_revision()
    #         rev.publish()
    #         return page_obj, False

    #     page = model(**values)
    #     parent_page.add_child(instance=page)
    #     page.save_revision().publish()
    #     return page, True
