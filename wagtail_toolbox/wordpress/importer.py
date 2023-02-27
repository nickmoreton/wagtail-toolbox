import requests


class Importer:
    ...


_session = requests.Session()


class Client:
    def __init__(self, host, url, endpoint):
        self.host = host
        self.url = url
        self.endpoint = endpoint
        try:
            self.response = _session.get(self.build_url)
            if not self.response.ok:
                raise Exception(self.response.text)
        except Exception as e:
            raise e

    @property
    def build_url(self):
        return f"{self.host}/{self.url}/{self.endpoint}"

    @property
    def is_paged(self):
        """Return True if the endpoint is paged, False otherwise."""

        return "X-WP-TotalPages" in self.response.headers

    @property
    def get_total_pages(self):
        """Return the total number of pages."""

        if self.is_paged:
            return int(self.response.headers["X-WP-TotalPages"])

        return 1

    @property
    def get_total_results(self):
        """Return the total number of results."""

        if "X-WP-Total" in self.response.headers:
            return int(self.response.headers["X-WP-Total"])

    @property
    def paged_endpoints(self):
        """Generate a list of URLs that can be fetched.
        The 'page' parameter is always appended to the URL.
        Returns:
            A list of URLs.
        Example:
            [
                "https://foo.com/endpoint/bar/baz?page=1",
                "https://foo.com/endpoint/bar/baz?page=2",
            ]
        """

        total_pages = self.get_total_pages

        return [f"{self.build_url}?page={index}" for index in range(1, total_pages + 1)]
