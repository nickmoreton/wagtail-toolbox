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
    process = subprocess.Popen(
        [command],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1000,
    )

    yield b"Start %b!\n" % command.encode("utf-8")

    for std in ["stdout", "stderr"]:
        for line in iter(getattr(getattr(process, std), "readline"), b""):
            try:
                yield line.rstrip() + b"\n"
            except KeyboardInterrupt:
                return


@login_required
@staff_member_required
@require_http_methods(["GET", "POST"])
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
            "title": "Import WordPress data",
        },
    )


# from config.utils import read_platform_config

# config = read_platform_config("wordpress")


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
                print("*****************")
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
