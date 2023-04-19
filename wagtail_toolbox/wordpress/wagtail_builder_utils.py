from bs4 import BeautifulSoup as bs4


def heading(html, **kwargs):
    """Builds a heading block from the html.

    Args:
        html (str): The html to parse.

    Returns:
        dict: The heading block.

    Example:
        >>> html = '<h1>Heading</h1>'
        >>> heading_block_builder(html)
        {
            'type': 'heading',
            'value': {
                'text': 'Heading',
                'importance': 'h1',
            },
        }

    Details:
        This will parse out all the h1-h6 tags but in config you
        may not be forwarding all of the tags.
    """

    soup = bs4(html, "html.parser").find_all(
        [f"h{i}" for i in range(1, 7)],
        recursive=True,
    )

    if not len(soup) or len(soup) > 1:
        return None

    element = soup[0]

    block_python = dict(
        type="heading",
        value=dict(
            text=element.text,
            importance=element.name,
        ),
    )

    return block_python


def block_quote(html, **kwargs):
    """Builds a block_quote block from the html.

    Args:
        html (str): The html to parse.

    Returns:
        dict: The block_quote block.

    Example:
        >>> html = '<blockquote>Quote</blockquote>'
        >>> block_quote(html)
        {
            'type': 'block_quote',
            'value': {
                'quote': 'Quote',
                'attribution': '',
                },
        }

    Details:
        This will parse out all the blockquote tags but in config you
        may not be forwarding all of the tags.

        This will also parse out the cite tag if it exists.

        If the cite tag does not exist then it will check for the cite
        attribute on the blockquote tag.

        If neither of those exist then the attribution will be an empty
        string.

        The cite tag is preferred over the cite attribute.
    """
    soup = bs4(html, "html.parser").find_all(
        "blockquote",
        recursive=True,
    )

    if not len(soup) or len(soup) > 1:
        return None

    element = soup[0]

    signatures = [
        "blockquote:p:",
        "blockquote:p:br:",
        "blockquote:p:strong:code:",
        "blockquote:p:strong:em:a:",
        "blockquote:p:cite:",
    ]
    has_signature = kwargs.get("signature", None) in signatures
    has_cite = "cite" in element.attrs or element.find("cite")

    quote = str(element.find()) if has_signature else element.text
    attribution = str(element.find("cite")) if has_cite else ""

    block_python = dict(
        type="block_quote",
        value=dict(
            quote=quote,
            attribution=attribution,
        ),
    )

    return block_python


def embed(html, **kwargs):
    """Builds an embed block from the html.

    Args:
        html (str): The html to parse.

    Returns:
        dict: The embed block.

    Example:
        >>> html = '<iframe src="https://www.youtube.com/embed/1234"></iframe>'
        >>> embed(html)
        {
            'type': 'embed',
            'value': 'https://youtu.be/1234',
        }

        Details:
            This will convert youtube embed links to youtu.be links.
    """
    soup = bs4(html, "html.parser").find_all(
        "iframe",
        recursive=True,
    )

    if not len(soup) or len(soup) > 1:
        return None

    element = soup[0]

    # custom parsing for youtu.be share links
    src = element["src"]
    if "youtube.com" in src:
        src = src.replace("embed/", "")
        src = src.replace("www.youtube.com", "youtu.be")
        src = src.split("?")[0]

    block_python = dict(
        type="embed",
        value=src,
    )

    return block_python


def description(html, **kwargs):
    """Builds a description a.k.a. definition list block from the html.

    Args:
        html (str): The html to parse.

    Returns:
        dict: The description block.

    Example:
        >>> html = '<dl><dt>Term</dt><dd>Description</dd></dl>'
        >>> description(html)
        {
            'type': 'description',
            'value': {
                'items': [
                    {
                        'term': 'Term',
                        'description': 'Description',
                    },
                ],
            },
        }

    Details:
        This will parse out all the dl tags but in config you
        may not be forwarding all of the tags.

        This will also parse out the dt and dd tags.
        If no dt tags are found then it will return None because it
        seems like a description block should have at least one term.
    """
    soup = bs4(html, "html.parser").find_all(
        "dl",
        recursive=True,
    )

    if not len(soup) or len(soup) > 1:
        return None

    if not soup[0].find_all("dt"):
        return None

    items = []
    for dt in soup[0].find_all("dt"):
        dd = dt.find_next_sibling("dd")
        items.append(
            dict(
                term=dt.text,
                description=dd.text,
            )
        ) if dd else None  # ignore if no dd

    block_python = (
        dict(
            type="description",
            value=dict(
                items=items,
            ),
        )
        if items
        else None
    )

    return block_python


def address(html, **kwargs):
    """Builds an address block from the html.

    Args:
        html (str): The html to parse.

    Returns:
        dict: The address block.

    Example:
        >>> html = '<address>123 Main St</address>'
        >>> address(html)
        {
            'type': 'address',
            'value': '123 Main St',
        }

    Details:
        This will parse out all the address tags but in config you
        may not be forwarding all of the tags.
    """
    soup = bs4(html, "html.parser").find_all(
        "address",
        recursive=True,
    )

    if not len(soup) or len(soup) > 1:
        return None

    element = soup[0]
    # print(str(element))

    block_python = dict(
        type="address",
        value=dict(
            address=str(element),
        ),
    )

    return block_python


def figure(html, **kwargs):
    return {
        "type": "raw_html",
        "value": html,
    }


def title(html, **kwargs):
    return {
        "type": "raw_html",
        "value": html,
    }


def pre(html, **kwargs):
    return {
        "type": "raw_html",
        "value": html,
    }


def table(html, **kwargs):
    return {
        "type": "raw_html",
        "value": html,
    }


def form(html, **kwargs):
    return {
        "type": "raw_html",
        "value": html,
    }


def rich_text(html, **kwargs):
    return {
        "type": "rich_text",
        "value": html,
    }


def raw_html(html, **kwargs):
    return {
        "type": "raw_html",
        "value": html,
    }


def null(html, **kwargs):
    return None
