from html.parser import HTMLParser


class DomTagSignatureMaker(HTMLParser):
    """Make a list of tag patterns from HTML

    Example 1:
        input = '<div>
            <p>
                <a href="#">Link</a></p></div>'
        output = ['div>p>a']

    Example 2:
        input = '<div>
            <p>
                <a href="#">Link</a></p></div>
        <div>
            <p>
                <a href="#">Link</a></p></div>'
        output = ['div>p>a'] there are no duplicates

    Example 3:
        input = '<div>
            <p>
                <a href="#">Link</a></p></div>
        <ul>
            <li>
                <a href="#">Link</a></li></ul>'
        output = ['div>p>a', 'ul>li>a']

    Example 4:
        input = '<div>
            <p>
                <a href="#">Link</a></p></div>
        <div>
            <p>
                <a href="#">Link</a></p></div>
        <ul>
            <li>
                <a href="#">Link</a></li></ul>'
        output = ['div>p>a', 'ul>li>a'] there are no duplicates

    The parsing result relies on the source HTML being well-formed in the respect that each top-level
    element/tag is a container for a single block of content that ultimately ends becoming a block or
    is part of a rich text block.

    e.g. this is not well-formed as the div with a class of 'container' is not considered to be relevant
    <div class="container">
        <div class="anchor" id="anchor-1">
            <p>
                <a href="http://example.com" class="link">Link</a></p></div>
        <div class="anchor" id="anchor-2">
            <p>
                <a href="http://example.com" class="link">Link</a></p></div>
        <ul class="list">
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        <div class="spacer"></div>
    </div>

    A method to promote the children of a 'container' type element to the top level is provided in each
    wordpress model `clean_content_html` method which is called during the import process.
    """

    def __init__(self, separator=">", include_attrs=False):
        super().__init__()
        self.tags = []
        self.tag_opens = []
        self.separator = separator
        self.include_attrs = include_attrs

    def handle_starttag(self, tag, attrs):
        if not self.include_attrs:
            self.tag_opens.append(tag)
        else:
            attr_string = ""
            for attr in sorted(attrs):
                attr_string += f"{attr[0]}={attr[1]},"
            if attr_string:
                self.tag_opens.append(f'{tag}[{attr_string.strip(",")}]')
            else:
                self.tag_opens.append(tag)

    def handle_endtag(self, tag):
        self.tags.append(self.separator.join(self.tag_opens))
        self.tag_opens = []

    def remove_empty(self):
        self.tags = [t for t in self.tags if t]

    def remove_duplicates(self):
        tags = self.tags.copy()
        self.tags = [tags[i] for i in range(len(tags)) if tags[i] not in tags[:i]]

    def append_separator(self, separator):
        self.tags = [f"{t}{separator}" for t in self.tags]

    def get_signatures(self, first_only=False):
        self.remove_empty()
        self.remove_duplicates()
        self.append_separator(self.separator)

        if not first_only:
            # self.tags is a list of tag signatures
            # useful when updating a look up table
            return self.tags
        # only return the first tag signature
        # useful when searching the look up table
        return self.tags[0]
