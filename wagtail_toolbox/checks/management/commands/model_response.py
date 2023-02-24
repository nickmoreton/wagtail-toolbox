import requests
from django.core.management.base import BaseCommand
from wagtail.models import Site


class Command(BaseCommand):
    """A command to run against a development site that is running and ready to accept requests.

    Requests are made to one single page of each page model for both
    the admin site (edit) and front end (view) and it reports the response codes.

    Page paths highlighted in `red`! Investigate the error.

    Params:

    --host: the hostname and port on your local machine
    --site_id: the id of the site you want run to tests against
    --username: the username of an admin account
    --password: the password of the admin account

    Run: python manage.py check_responses
    """

    help = "Check if admin response is 200 for each page content type when entering edit mode."

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            default="http://127.0.0.1:8000",
            help="The URL to check",
        )
        parser.add_argument(
            "--site_id",
            default=None,
            help="The ID of the site to check",
        )
        parser.add_argument(
            "--username",
            default="admin",
            help="The username to use",
        )
        parser.add_argument(
            "--password",
            default="admin",
            help="The password to use",
        )

    def handle(self, *args, **options):
        with requests.Session() as session:
            # Login
            url = f"{options['host']}/admin/login/"

            try:
                session.get(url)
            except requests.exceptions.ConnectionError:
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not connect to {options['host']}. Is the server running?"
                    )
                )
                return
            except requests.exceptions.InvalidSchema:
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not connect to {options['host']}. Invalid schema"
                    )
                )
                return
            except requests.exceptions.MissingSchema:
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not connect to {options['host']}. Missing schema"
                    )
                )
                return

            csrftoken = session.cookies["csrftoken"]
            login_data = dict(
                username=options["username"],
                password=options["password"],
                csrfmiddlewaretoken=csrftoken,
                next="/admin/",
            )

            logged_in = session.post(url, data=login_data).content

            if "Forgotten password?" in logged_in.decode("utf-8"):
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not log in to {options['host']}. Is the username and password correct?"
                    )
                )
                exit()

            try:
                if options["site_id"]:
                    site = Site.objects.get(id=options["site_id"])
                else:
                    site = Site.objects.get(is_default_site=True)
            except Site.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not find a site with id {options['site_id']}."
                    )
                )
                return

            pages = (
                site.root_page.get_descendants(inclusive=True)
                .defer_streamfields()
                .specific()
            )

            track_class_names = []
            result = []

            for page in pages:
                class_name = page.__class__.__name__
                if class_name not in track_class_names:
                    track_class_names.append(class_name)
                    result.append(
                        {
                            "title": page.title,
                            "url": f"{options['host']}{page.url}",
                            "id": page.id,
                            "editor_url": f"{options['host']}/admin/pages/{page.id}/edit/",
                            "class_name": class_name,
                        }
                    )

            self.stdout.write(f"Checking {len(result)} content types...")
            self.stdout.write("============================")

            for count, content_type in enumerate(sorted(track_class_names)):
                if count <= 8:
                    self.stdout.write(f" {count + 1}. {content_type}")
                else:
                    self.stdout.write(f"{count + 1}. {content_type}")
            self.stdout.write("============================\n")

            # Check the admin url's
            for page in result:
                self.stdout.write(f"{page['title']} ( {page['class_name']} ) ↓\n")

                response = session.get(page["editor_url"])
                if response.status_code != 200:
                    self.stderr.write(
                        self.style.ERROR(
                            f"{page['editor_url']} ← {response.status_code}"
                        )
                    )
                else:
                    self.stdout.write(self.style.SUCCESS(f"{page['editor_url']} ← 200"))

                response = session.get(page["url"])
                if response.status_code != 200:
                    if response.status_code == 404:
                        self.stderr.write(
                            self.style.WARNING(
                                f"{page['url']} ← {response.status_code} probably a draft page"
                            )
                        )
                    else:
                        self.stderr.write(
                            self.style.ERROR(f"{page['url']} ← {response.status_code}")
                        )
                else:
                    self.stdout.write(self.style.SUCCESS(f"{page['url']} ← 200"))

                self.stdout.write("-\n")
