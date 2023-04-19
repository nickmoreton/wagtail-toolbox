import responses
from django.test import TestCase

from wagtail_toolbox.wordpress.api_client import Client


class TestClient(TestCase):
    """Test the Client class."""

    def setUp(self):
        self.test_url = "https://example.com/wp-json/wp/v2/posts"
        self.header_total_pages = "X-WP-TotalPages"
        self.header_total_results = "X-WP-Total"

    @responses.activate
    def test_get(self):
        """Test that the get method returns the correct JSON."""
        responses.add(
            responses.GET,
            self.test_url,
            status=200,
            json=[{"foo": "bar"}],
        )
        client = Client(self.test_url)
        self.assertEqual(client.get(self.test_url), [{"foo": "bar"}])

    @responses.activate
    def test_failed_get(self):
        """Test that the get method raises an exception if the request fails."""
        responses.add(
            responses.GET, self.test_url, body=Exception("Error fetching endpoint")
        )
        client = Client(self.test_url)
        with self.assertRaises(Exception):
            client.get(self.test_url)

    @responses.activate
    def test_get_total_pages(self):
        """Test that the get_total_pages property returns the correct number of pages."""
        responses.add(
            responses.GET,
            self.test_url,
            status=200,
            headers={self.header_total_pages: "2"},
        )
        client = Client(self.test_url)
        self.assertEqual(client.get_total_pages, 2)

    @responses.activate
    def test_get_total_results(self):
        """Test that the get_total_results property returns the correct number of results."""
        responses.add(
            responses.GET,
            self.test_url,
            status=200,
            headers={self.header_total_results: "2"},
        )
        client = Client(self.test_url)
        self.assertEqual(client.get_total_results, 2)

    @responses.activate
    def test_is_paged(self):
        """Test that the is_paged property returns True if the endpoint is paged."""
        responses.add(
            responses.GET,
            self.test_url,
            status=200,
            headers={self.header_total_pages: "2"},
        )
        client = Client(self.test_url)
        self.assertTrue(client.is_paged)

    @responses.activate
    def test_is_not_paged(self):
        """Test that the is_paged property returns False if the endpoint is not paged."""
        responses.add(
            responses.GET,
            self.test_url,
            status=200,
        )
        client = Client(self.test_url)
        self.assertFalse(client.is_paged)

    @responses.activate
    def test_paged_endpoints(self):
        """Test that the paged_endpoints property returns a list of URLs."""
        responses.add(
            responses.GET,
            self.test_url,
            status=200,
            headers={self.header_total_pages: "2"},
        )
        client = Client(self.test_url)
        for _ in client.paged_endpoints:
            self.assertEqual(
                client.paged_endpoints,
                [
                    f"{self.test_url}?page=1",
                    f"{self.test_url}?page=2",
                ],
            )
