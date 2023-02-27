from django.shortcuts import render

from .models import WordpressSettings


def import_wordpress_data_view(request):
    # probably need to add a form here to select the data to import
    wp_settings = WordpressSettings.for_request(request)
    endpoints = wp_settings.get_endpoints()
    return render(
        request, "wordpress/admin/import_wordpress_data.html", {"endpoints": endpoints}
    )
