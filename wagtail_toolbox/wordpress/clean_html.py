from bs4 import BeautifulSoup


class HTMLCleaner:
    def __init__(self, html_data, tags_to_remove=None):
        self.html_data = html_data
        if not tags_to_remove:
            self.tags_to_remove = ["div"]
        else:
            self.tags_to_remove = tags_to_remove

    def clean_html(self):
        soup = BeautifulSoup(self.html_data, "html.parser")
        # find all div tags and remove them while keeping their contents
        for div in soup.find_all(self.tags_to_remove):
            div.unwrap()
        return str(soup)


if __name__ == "__main__":
    from pathlib import Path

    cwd = Path.cwd()
    fixtures_dir = cwd / "tests" / "fixtures"
    with open(fixtures_dir / "test_cleaner.html", "r") as f:
        html_data = f.read()

    html_parser = HTMLCleaner(html_data)
    output = html_parser.clean_html()

    # some quick tests
    assert "<div>" not in output
    assert "<p>This page tests how the theme displays the columns block." in output
    assert (
        "<p>This is the second column block. It has <strong>3</strong> columns.</p>"
        in output
    )
    assert (
        "<p>To change the number of columns, select the column block to open the settings panel."
        in output
    )
    assert """<figure class="wp-block-media-text__media">""" in output

    html_parser = HTMLCleaner(html_data, tags_to_remove=["p", "div", "figure"])
    output = html_parser.clean_html()

    # some quick tests
    assert "<p>" not in output
    assert "<div>" not in output
    assert "<figure>" not in output

    html_parser = HTMLCleaner(html_data, tags_to_remove=["p", "figure", "strong"])
    output = html_parser.clean_html()

    # some quick tests
    assert "<p>" not in output
    assert "<strong>" not in output
    assert "<figure>" not in output
    assert "div" in output
