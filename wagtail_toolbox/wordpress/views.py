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

from .models import WordpressHost


@login_required
@staff_member_required
@require_http_methods(["GET"])
def run_import(request):
    if (
        not request.GET.get("command")
        or not request.GET.get("url")
        or not request.GET.get("model")
    ):
        return HttpResponse("Missing parameters for command, url or model.")
    command = request.GET.get("command")
    url = request.GET.get("url")
    model = request.GET.get("model")

    def stream_response():
        yield b"Start %b!\n===============\n" % command.encode("utf-8")
        process = subprocess.Popen(
            ["python", "manage.py", f"{command}", f"{url}", f"{model}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for line in iter(process.stdout.readline, b""):
            yield line.decode("utf-8")

        process.stdout.close()
        process.wait()
        yield b"=============\nEnd %b!\n" % command.encode("utf-8")

    return StreamingHttpResponse(stream_response())


def import_wordpress_data_view(request):
    endpoints = WordpressHost.for_request(request=request).wordpress_endpoints.all()
    return render(
        request,
        "wordpress/admin/import_wordpress_data.html",
        {
            "runner": reverse("run-import"),
            "command": "importer",
            "endpoints": endpoints,
            "title": "Import Data",
        },
    )


@login_required
@staff_member_required
@require_http_methods(["GET", "POST"])
def run_transfer(request):
    if not request.GET.get("command"):
        return HttpResponse("Missing parameters for command.")
    command = request.GET.get("command")
    source_model = request.GET.get("source-model")
    target_model = request.GET.get("target-model")
    primary_keys = ",".join(request.GET.getlist("primary-keys"))

    def stream_response():
        yield b"Start %b!\n===============\n" % command.encode("utf-8")
        process = subprocess.Popen(
            [
                "python",
                "manage.py",
                f"{command}",
                f"{source_model}",
                f"{target_model}",
                f"{primary_keys}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for line in iter(process.stdout.readline, b""):
            yield line.decode("utf-8")

        process.stdout.close()
        process.wait()
        yield b"=============\nEnd %b!\n" % command.encode("utf-8")

    return StreamingHttpResponse(stream_response())


def transfer_wordpress_data_view(request):
    errors = []

    if hasattr(settings, "WPI_TARGET_BLOG_INDEX"):
        if (
            not settings.WPI_TARGET_BLOG_INDEX[0]
            or not settings.WPI_TARGET_BLOG_INDEX[1]
        ):
            errors.append("WPI_TARGET_BLOG_INDEX is not defined correctly in settings.")
    else:
        errors.append("WPI_TARGET_BLOG_INDEX is not defined in settings.")

    if not hasattr(settings, "WPI_ADMIN_TARGET_MODELS") or not hasattr(
        settings, "WPI_TARGET_MAPPING"
    ):
        if not hasattr(settings, "WPI_TARGET_MAPPING"):
            errors.append("WPI_TARGET_MAPPING is not defined in settings.")
        if not hasattr(settings, "WPI_ADMIN_TARGET_MODELS"):
            errors.append("WPI_ADMIN_TARGET_MODELS is not defined in settings.")
        return render(
            request,
            "wordpress/admin/transfer_wordpress_data.html",
            {
                "errors": errors,
                "title": "Transfer Data",
                "description": "Transfer data from WordPress to Wagtail.",
            },
        )
    else:
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
                "runner": reverse("run-transfer"),
                "command": "transfer",
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
