import responses
from django.test import TestCase

from wagtail_toolbox.wordpress.api_client import Client


class TestClient(TestCase):
    @responses.activate
    def test_build_url(self):
        """Test that the build_url property returns the correct URL."""
        responses.add(
            responses.GET, "https://example.com/wp-json/wp/v2/posts", status=200
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        self.assertEqual(client.build_url, "https://example.com/wp-json/wp/v2/posts")

    @responses.activate
    def test_get_total_pages(self):
        """Test that the get_total_pages property returns the correct number of pages."""
        responses.add(
            responses.GET,
            "https://example.com/wp-json/wp/v2/posts",
            status=200,
            headers={"X-WP-TotalPages": "2"},
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        self.assertEqual(client.get_total_pages, 2)

    @responses.activate
    def test_get_total_results(self):
        """Test that the get_total_results property returns the correct number of results."""
        responses.add(
            responses.GET,
            "https://example.com/wp-json/wp/v2/posts",
            status=200,
            headers={"X-WP-Total": "2"},
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        self.assertEqual(client.get_total_results, 2)

    @responses.activate
    def test_is_paged(self):
        """Test that the is_paged property returns True if the endpoint is paged."""
        responses.add(
            responses.GET,
            "https://example.com/wp-json/wp/v2/posts",
            status=200,
            headers={"X-WP-TotalPages": "2"},
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        self.assertTrue(client.is_paged)

    @responses.activate
    def test_is_not_paged(self):
        """Test that the is_paged property returns False if the endpoint is not paged."""
        responses.add(
            responses.GET,
            "https://example.com/wp-json/wp/v2/posts",
            status=200,
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        self.assertFalse(client.is_paged)

    @responses.activate
    def test_paged_endpoints(self):
        """Test that the paged_endpoints property returns a list of URLs."""
        responses.add(
            responses.GET,
            "https://example.com/wp-json/wp/v2/posts",
            status=200,
            headers={"X-WP-TotalPages": "2"},
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        for url in client.paged_endpoints:
            self.assertEqual(
                client.paged_endpoints,
                [
                    "https://example.com/wp-json/wp/v2/posts?page=1",
                    "https://example.com/wp-json/wp/v2/posts?page=2",
                ],
            )

    @responses.activate
    def test_get(self):
        """Test that the get method returns the correct JSON."""
        responses.add(
            responses.GET,
            "https://example.com/wp-json/wp/v2/posts",
            status=200,
            json={"foo": "bar"},
        )
        client = Client("https://example.com/wp-json/wp/v2/posts")
        self.assertEqual(
            client.get("https://example.com/wp-json/wp/v2/posts"), {"foo": "bar"}
        )
