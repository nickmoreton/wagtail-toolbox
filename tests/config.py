class TestConfig:
    """Return some test config properties"""

    def __init__(self):
        self.block_patterns = self.get_wpi_block_patterns()
        self.richtext_patterns = self.get_wpi_richtext_patterns()

    def get_wpi_block_patterns(self):
        return {
            "address:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "address:br:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "audio:source:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "blockquote:p:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "blockquote:p:br:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "blockquote:p:strong:code:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "blockquote:p:strong:em:a:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "div:": [  # convert to paragraph
                "wagtail_toolbox.wordpress.content_cleaner.convert_to_paragraph"
            ],
            "div:a:": [  # convert to paragraph
                "wagtail_toolbox.wordpress.content_cleaner.convert_to_paragraph"
            ],
            "div:a:br:": [  # convert to paragraph
                "wagtail_toolbox.wordpress.content_cleaner.convert_to_paragraph"
            ],
            "div:div:ol:li:": [  # convert to paragraph, remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:div:p:": [  # convert to paragraph, remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:div:p:em:": [  # convert to paragraph, remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:div:p:strong:": [  # convert to paragraph, remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:figure:a:img:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:figure:div:a:img:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:figure:img:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:label:": ["wagtail_toolbox.wordpress.content_cleaner.promote_content"],
            "div:p:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:p:strong:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:table:caption:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "div:video:": [  # remove top level div
                "wagtail_toolbox.wordpress.content_cleaner.promote_content"
            ],
            "dl:dt:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:a:img:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:audio:": [  # remove top level figure
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:blockquote:p:": [  # remove top level figure
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:div:": [  # remove top level figure and convert to paragraph
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:div:blockquote:p:a:": [  # remove top level figure and div
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:div:iframe:": [  # remove top level figure and div
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:img:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:table:tbody:tr:td:": [  # remove top level figure
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:ul:li:figure:a:img:": [  # needs a block, looks like a gallery
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:ul:li:figure:img:": [  # needs a block, looks like a gallery
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "figure:video:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "form:label:": [  # needs a block looks like a form
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "h1:": [  # needs a block, looks like a title
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "pre:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "pre:br:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "pre:cite:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "pre:code:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "table:tbody:tr:td:": [  # needs a block
                "wagtail_toolbox.wordpress.content_cleaner.dont_clean"
            ],
            "table:thead:tr:th:": [  # needs a block
                "wagtail_toolbox[.wordpress.content_cleaner.dont_clean"
            ],
        }

    def get_wpi_richtext_patterns(self):
        return [
            "p",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "blockquote",
            "a",
            "img",
            "strong",
            "em",
            "br",
            "hr",
            # "code",
            "sub",
            "sup",
            "del",
        ]
