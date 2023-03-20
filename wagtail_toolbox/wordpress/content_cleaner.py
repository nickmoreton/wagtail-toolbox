from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.module_loading import import_string


class ContentCleaner:
    def __init__(self, content):
        """Content cleaner looks for top level tags that can't be use directly in a richtext field
        and converts them to a format that can be used later, most likely a block."""

        self.soup = BeautifulSoup(content, "html.parser")
        self.tag_list = []
        if hasattr(settings, "WPI_BLOCK_PATTERNS"):
            self.block_patterns = settings.WPI_BLOCK_PATTERNS
        if hasattr(settings, "WPI_RICHTEXT_PATTERNS"):
            self.dont_clean = settings.WPI_RICHTEXT_PATTERNS

    def clean(self):
        for tag in self.soup.findChildren(recursive=False):
            tag_pattern = f"{tag.name}:"
            if tag.name in self.dont_clean:
                self.tag_list.append(f"{tag}")
                continue
            for child in tag.findChildren(recursive=True):
                tag_pattern += f"{child.name}:"

            for pattern in self.block_patterns:
                if tag_pattern.startswith(pattern):
                    clean_action = import_string(self.block_patterns[pattern][0])
                    pre_actions = [
                        import_string(action)
                        for action in self.block_patterns[pattern][1:]
                    ]
                    self.tag_list.append(clean_action(tag, pre_actions))

        return "".join(self.tag_list)


def dont_clean(tag, pre_actions=[]):
    return f"{tag}"


def promote_content(tag, pre_actions=[]):
    return f"{tag.children}"


def convert_to_paragraph(tag, pre_actions=[]):
    return f"<p>{tag.text}</p>"


# def convert_linked_image(tag):
#     return f'<a href="{tag.a["href"]}"><img src="{tag.img["src"]}"></a>'


# def convert_image(tag):
#     return f'<img src="{tag.img["src"]}">'
