# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.decorators import login_required
# from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import WordpressSettings

# from django.views.decorators.http import require_http_methods


def import_wordpress_data_view(request):
    # probably need to add a form here to select the data to import
    wp_settings = WordpressSettings.for_request(request)
    endpoints = wp_settings.get_endpoints()
    return render(
        request,
        "wordpress/admin/import_wordpress_data.html",
        {
            "endpoints": endpoints,
            "command_view_url": reverse("run_management_command"),
        },
    )
