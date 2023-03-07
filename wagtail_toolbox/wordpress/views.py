import subprocess

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

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
        },
    )
