from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from wagtail.models import Page


class Command(BaseCommand):
    """
    A command to report on page types in the project.

    Params:

    --index: the id of the content type you want to report on.

    Run: python manage.py report_page_types
    """

    help = """Report on page types in the project.
        If no index is given, report on all page types.
        If an index is given, report on the page types with that index.
        """

    def add_arguments(self, parser):
        parser.add_argument(
            "--index",
            "-i",
            type=int,
            default=0,
            help="The #index of the page type to report on.",
        )

    def handle(self, *args, **options):
        if not options["index"]:
            self.stdout.write(self.style.WARNING(HELP_TEXT_INITIAL))

            content_types = ContentType.objects.filter(
                app_label__in=get_apps_for_report()
            ).order_by("model", "app_label")

            data = [
                [
                    content_type.id,
                    content_type.model,
                    content_type.app_label,
                ]
                for content_type in content_types
            ]

            self.print_content_type_list(data)

            return

        self.stdout.write(HELP_TEXT_FINAL)

        content_type = ContentType.objects.get(id=options["index"])
        pages = Page.objects.filter(content_type_id=options["index"]).order_by("title")

        self.print_page_edit_links(pages, content_type=content_type)

    def print_content_type_list(self, data=[]):
        headers = ["C-Type ID", "Model", "App"]
        self.stdout.write(f"{headers[0]} {headers[1]: <46} {headers[2]: <20}")
        self.stdout.write(header_divider(73))
        for row in data:
            self.stdout.write(f"{row[0]: >9} {row[1]: <46} {row[2]: <20} ")

    def print_page_edit_links(self, data=[], content_type=None):
        headers = [f"Page ({content_type})", "Edit URL"]
        self.stdout.write(f"{headers[0]: <35} {headers[1]}")
        self.stdout.write(header_divider(70))
        for page in data:
            title = page.title[:30] + "..." if len(page.title) > 30 else page.title
            self.stdout.write(f"{title: <35} {get_page_edit_url(page.id)}")


HELP_TEXT_INITIAL = """
To use this command:
Run it with the --index option followed by the C-Type ID of the content type you want to list.
Example: python manage.py report_page_types [-i,--index] 21

"""

HELP_TEXT_FINAL = """
The links here can be cmd/ctrl clicked to open in a browser.

"""

BASE_URL = getattr(settings, "WAGTAILADMIN_BASE_URL", "http://localhost:8000")

# add any apps you want to exclude from the report here
EXCLUDED_APPS = ["taggit"]

# If your apps are prefixed with a common module string, set it here.
APPS_PREFIX = "testapp"


def get_apps_for_report():
    """Return a list of apps we care about for the page types report."""
    if not APPS_PREFIX:
        apps = [
            app
            for app in settings.INSTALLED_APPS
            if not app.split(".")[0] in EXCLUDED_APPS
        ]
        return apps

    return [
        app.split(".")[1]
        for app in settings.INSTALLED_APPS
        if app.startswith(APPS_PREFIX)
    ]


def get_page_edit_url(id):
    return f"{BASE_URL}/admin/pages/{id}/edit/"


def header_divider(num):
    return "-" * num
