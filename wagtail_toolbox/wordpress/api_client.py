import sys

import requests

_session = requests.Session()


class Client:
    """A simple client for the WordPress REST API.
    On been instantiated, the client will fetch the first page of the endpoint.

    It will set the following class properties that can be used to determine:
    - is_paged: True if the endpoint is paged, False otherwise.
    - total_pages: The total number of pages.
    - total_results: The total number of results.
    - paged_endpoints: A list of URLs that can be fetched.

    Calling the get() method will return the JSON response from the endpoint.
    """

    def __init__(self, url):
        self.url = url

        try:
            self.response = _session.get(self.url)
            sys.stdout.write(f"Fetching {self.url}\n")
        except Exception as e:
            sys.stdout.write(f"Error: {e}\n")

    def get(self, url):
        try:
            return _session.get(url).json()
        except Exception as e:
            raise e

    @property
    def is_paged(self):
        """Return True if the endpoint is paged, False otherwise."""
        return "X-WP-TotalPages" in self.response.headers

    @property
    def get_total_pages(self):
        """Return the total number of pages."""
        return int(self.response.headers["X-WP-TotalPages"])

    @property
    def get_total_results(self):
        """Return the total number of results."""
        return int(self.response.headers["X-WP-Total"])

    @property
    def paged_endpoints(self):
        # TODO: This should be a generator.
        # and the Client would be used differently
        # in the WordPressImport class.
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

        return [f"{self.url}?page={index}" for index in range(1, total_pages + 1)]
