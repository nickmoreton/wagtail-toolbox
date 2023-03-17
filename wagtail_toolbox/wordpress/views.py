import json
import subprocess
from urllib.parse import urljoin, urlparse

from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import View

from .models import WordpressSettings


def run_command(command):
    # TODO: This is a bit of a hack, but it works for now, to a point.
    # but it's not a streaming response as I'd like it to be.
    process = subprocess.run(
        [command],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    yield b"Start %b!\n" % command.encode("utf-8")

    for line in process.stdout.splitlines():
        yield line.encode("utf-8") + b"\n"
    for line in process.stderr.splitlines():
        yield line.encode("utf-8") + b"\n"


@login_required
@staff_member_required
@require_http_methods(["POST"])
def run_import(request):
    if request.method == "POST":
        host = request.POST.get("host")
        url = request.POST.get("url")
        model = request.POST.get("model")
        command = f"python3 manage.py import {host} {url} {model}"

        return StreamingHttpResponse(run_command(command))


def import_wordpress_data_view(request):
    wp_settings = WordpressSettings.for_request(request=request)
    endpoints = wp_settings.get_endpoints()
    host = settings.WPI_HOST
    return render(
        request,
        "wordpress/admin/import_wordpress_data.html",
        {
            "run_command_url": reverse("run_import"),
            "host": host,
            "endpoints": endpoints,
            "title": "Import Data",
            "description": "Import data from a WordPress site for processing and transfer it to Wagtail.",
        },
    )


@login_required
@staff_member_required
@require_http_methods(["GET", "POST"])
def run_transfer(request):
    if request.method == "POST":
        source_model = request.POST.get("source-model")
        target_model = request.POST.get("target-model")
        primary_keys = ",".join(request.POST.getlist("primary-keys"))
        command = (
            f"python3 manage.py transfer {source_model} {target_model} {primary_keys}"
        )
        return StreamingHttpResponse(run_command(command))


def transfer_wordpress_data_view(request):
    if hasattr(settings, "WPI_ADMIN_TARGET_MODELS"):
        models = []
        for model in settings.WPI_ADMIN_TARGET_MODELS:
            wagtail_model = apps.get_model(model[0])
            wordpress_model = apps.get_model(model[1])
            models.append(
                {
                    "wagtail": {
                        "model": f"{wagtail_model._meta.app_label}.{wagtail_model.__name__}",
                        "name": wagtail_model.__name__,
                        "count": wagtail_model.objects.count(),
                        "source": [
                            {"id": x.id, "title": x.get_title}
                            for x in wordpress_model.objects.all()
                        ],
                        "target": f"{wagtail_model._meta.app_label}.{wagtail_model.__name__}",
                    },
                    "wordpress": {
                        "model": f"{wordpress_model._meta.app_label}.{wordpress_model.__name__}",
                        "name": wordpress_model.__name__,
                        "count": wordpress_model.objects.count(),
                        "records": [
                            {
                                "id": x.id,
                                "title": x.get_title,
                            }
                            for x in wordpress_model.objects.all()
                        ],
                        "target": f"{wagtail_model._meta.app_label}.{wagtail_model.__name__}",
                    },
                }
            )

    return render(
        request,
        "wordpress/admin/transfer_wordpress_data.html",
        {
            "title": "Transfer Data",
            "description": "Transfer data from WordPress to Wagtail.",
            "models": models,
            # "models_json": models_json,
            "transfer_command_url": reverse("run_transfer"),
        },
    )


class ApiView(View):
    """API view for the WordPress importer."""

    def get(self, request, *args, **kwargs):
        full_url = urlparse(request.build_absolute_uri())
        scheme = full_url.scheme
        host = full_url.netloc
        path = full_url.path.split("/")
        self.api_root_url = urljoin(f"{scheme}://{host}", "/wordpress-api/")
        objects_values = settings.WPI_API_MODELS

        if not path[2]:  # api root
            return self.api_root(objects_values)

        if not path[2] in objects_values:
            return HttpResponse(
                [
                    {
                        "error": f"Model '{path[2]}' does not exist.",
                    }
                ],
                status=404,
            )

        model = apps.get_model("wordpress", path[2])

        try:
            # /api/model/related
            if path[3] and path[3] == "related" and not path[4]:
                return self.api_model(
                    model,
                    related=True,
                )
            # /api/model/related/id
            elif path[3] and path[3] == "related" and path[4]:
                return self.api_model(
                    model,
                    related=True,
                    id=path[4],
                )
            else:
                return HttpResponseRedirect(self.api_root_url)

        except IndexError:
            return self.api_model(model)

    def api_root(self, objects_values):
        data = []
        for object in objects_values:
            model = apps.get_model("wordpress", object)
            model_name = model.__name__
            objects = model.objects.all()
            objects_list = [
                f"{self.api_root_url}{model_name.lower()}/related/{obj.id}"
                for obj in objects
            ]
            data.append(
                {
                    "model": model_name,
                    "url": f"{self.api_root_url}{model_name.lower()}",
                    "url_with_related": f"{self.api_root_url}{model_name.lower()}/related",
                    "objects": objects_list,
                }
            )

        out = json.dumps(data)
        return HttpResponse(out, content_type="application/json")

    def api_model(self, model, related=False, id=None):
        qs = model.objects.all()

        if not related:
            data = json.loads(serializers.serialize("json", qs))

        else:
            if not id:
                foreign_key_fields = [
                    f.name
                    for f in model._meta.fields
                    if f.get_internal_type() in ["ForeignKey"]
                ]

                data = []

                for item in qs:
                    item_dict = json.loads(serializers.serialize("json", [item])[1:-1])

                    for field in foreign_key_fields:
                        # parse the foreign key fields
                        # and add to the item_dict

                        if field in foreign_key_fields:
                            try:
                                obj_class = apps.get_model(
                                    "wordpress",
                                    getattr(item, field).__class__.__name__.lower(),
                                )
                                obj = obj_class.objects.get(id=getattr(item, field).id)
                                item_dict["fields"][field] = json.loads(
                                    serializers.serialize("json", [obj])
                                )
                            except LookupError:
                                pass

                    for field in item._meta.many_to_many:
                        # parse the many to many fields
                        # and add to the item_dict
                        all = getattr(item, field.name).all()
                        if all:
                            item_dict["fields"][field.name] = []
                        for obj in all:
                            item_dict["fields"][field.name].append(
                                json.loads(serializers.serialize("json", [obj]))
                            )

                    data.append(item_dict)
            else:
                item = qs.get(id=id)
                item_dict = json.loads(serializers.serialize("json", [item])[1:-1])

                for field in item._meta.many_to_many:
                    # parse the many to many fields
                    # and add to the item_dict
                    all = getattr(item, field.name).all()
                    if all:
                        item_dict["fields"][field.name] = []
                    for obj in all:
                        item_dict["fields"][field.name].append(
                            json.loads(serializers.serialize("json", [obj]))
                        )

                data = item_dict

        return HttpResponse(json.dumps(data), content_type="application/json")
