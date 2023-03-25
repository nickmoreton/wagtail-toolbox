from bs4 import BeautifulSoup as bs4
from django.utils.module_loading import import_string


class ContentCleaner:
    """
    Content cleaner converts top level tags that can't be used directly in a richtext field.

    params:
        patterns: dict of tag signatures and their actions
        patterns = {
            "div:": {
                "action": "promote_child_tag",
                "kwargs": {"depth": 0},
            },
            "div:div:": {
                "action": "promote_child_tag",
                "kwargs": {"depth": 1},
            },
            "div:a:": {
                "action": "promote_child_tag",
                "kwargs": {"depth": 1},
            },
        }

    returns:
        a string representing the new html content where the top level tags have been cleaned
    """

    def __init__(self, patterns=None):
        self.patterns = patterns or {}
        self.tag_list = []

    def get_clean_actions(self, tag):
        for pattern in self.patterns:
            if pattern == tag:
                actions = self.patterns[pattern].get("actions", None)
                for action in actions:
                    return action["clean"] if "clean" in action else None

    def get_cleaned_content(self, clean_actions, tag_string):
        cleaned = str()
        for clean_action in clean_actions:
            for action, kwargs in clean_action.items():
                try:
                    clean_function = import_string(action)
                except ImportError:
                    # action is a method on this class
                    clean_function = getattr(self, action)

                cleaned = clean_function(tag_string, **kwargs)

        return cleaned

    def clean(self, content):
        soup = bs4(content, "html.parser")
        stack = [soup]

        for node in soup.descendants:
            if node.name is None:
                continue
            stack.append(node)

            tag_pattern = self.make_tag_signature(node)
            print(tag_pattern)
            clean_actions = self.get_clean_actions(tag_pattern)

            if clean_actions:
                cleaned = self.get_cleaned_content(clean_actions, node)
                node.replace_with(cleaned)
            else:
                continue

        return soup

    # def clean(self, content):
    #     # only interested in the top level tags
    #     soup = bs4(content, "html.parser").findChildren(recursive=False)

    #     for tag in soup:
    #         tag_pattern = self.make_tag_signature(tag)
    #         clean_actions = self.get_clean_actions(tag_pattern)

    #         if clean_actions:
    #             cleaned = self.get_cleaned_content(clean_actions,tag)
    #             tag.i.replace_with(cleaned)
    #         else:
    #             continue

    #     return soup

    def make_tag_signature(self, soup):
        """
        Constructs a signature string for a BeautifulSoup tag and its children.

        Args:
        - soup: A BeautifulSoup object representing the tag to generate a
                signature for.

        Returns:
        - A string representing the signature of the given tag and its children.
        The signature consists of the names of the tag and its descendants,
        separated by colons (':'), in the order in which they are encountered
        during a depth-first traversal of the tree.
        """
        signature = f"{soup.name}:"
        current = soup.find()
        while current:
            signature += f"{current.name}:"
            current = current.find() if current.find() else False
        return signature

    def promote_child(self, soup, **kwargs):
        """
        Promotes a child of a given BeautifulSoup object to be the new root,
        after traversing a specified number of levels down the tree.

        Args:
        - soup: A BeautifulSoup object.
        - **kwargs: Additional keyword arguments. Currently supported:
            - depth: An integer representing the number of levels to traverse
                    down the tree before promoting a child.

        Returns:
        - A BeautifulSoup object representing the first non-empty child found
        after traversing the specified number of levels down the tree.
        If the specified number of levels is greater than the depth of the tree
        or no non-empty child is found, the original soup object is returned.
        """
        depth = kwargs.get("depth", 0)

        for _ in range(depth):
            children = soup.findChildren(recursive=False)
            if len(children) == 0:
                break
            soup = children[0]

        return soup.findChild(recursive=False)

    def make_paragraph(self, soup, **kwargs):
        """Wrap the content of the provided BeautifulSoup tag with a new 'p' tag,
        effectively turning it into a paragraph. The top level tag of the input soup
        is removed.

        Args:
            soup: A BeautifulSoup tag.
            kwargs: Additional keyword arguments (unused).

        Returns:
            A BeautifulSoup tag with the content wrapped in a new 'p' tag.
        """
        soup = soup.string.wrap(soup.new_tag("p"))
        return soup
