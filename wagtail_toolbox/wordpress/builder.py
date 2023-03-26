from bs4 import BeautifulSoup as bs4

# conf_fallback_block,; conf_html_tags_to_blocks,; conf_promote_child_tags,
from wagtail_toolbox.wordpress.builder_utils import make_tag_signature

# from django.utils.module_loading import import_string


class BlockBuilder:
    def __init__(self):
        # self.soup = BeautifulSoup(value, "lxml")
        # self.block_tags = block_tags
        # print(self.block_tags)
        # self.logged_items = {"processed": 0, "imported": 0, "skipped": 0, "items": []}
        # self.node = node
        # self.logger = logger
        self.blocks = []  # for each page this holds the sequence of StreamBlocks

    # def promote_child_tags(self):
    #     """
    #     Some HTML tags that can be at the top level, e.g. the parent is the
    #     body when using BS4 are getting placed inside or existed inside other HTML tags.
    #     We pull out these HTML tags and move them to the top level.
    #     returns: None
    #         but modifies the page soup
    #     """
    #     config_promote_child_tags = conf_promote_child_tags()
    #     promotee_tags = config_promote_child_tags["TAGS_TO_PROMOTE"]
    #     removee_tags = config_promote_child_tags["PARENTS_TO_REMOVE"]

    #     for promotee in promotee_tags:
    #         promotees = self.soup.findAll(promotee)
    #         for promotee in promotees:
    #             if promotee.parent.name in removee_tags:
    #                 promotee.parent.replace_with(promotee)

    # def get_builder_function(self, element):
    #     """
    #     params
    #         element: an HTML tag
    #     returns:
    #         a function to parse the block from configuration
    #     """

    #     tag_signature = make_tag_signature(element)
    #     print(tag_signature)
    # Detecting standard blocks to tags
    # try:
    #     builder = conf_html_tags_to_blocks()[element.name]
    #     return import_string(builder)
    # except KeyError:
    #     pass

    # registered shortcode handlers custom HTML tags
    # conf_custom_tags = {}
    # for handler in SHORTCODE_HANDLERS:
    #     cls = handler()
    #     conf_custom_tags[cls.element_name] = handler

    # if element.name in conf_custom_tags:
    #     handler = conf_custom_tags[element.name]
    #     # Return the method, so we can call it later like a function that takes a
    #     # single argument.
    #     return handler().construct_block

    def build(self, html, block_tags):
        # try:
        #     soup = self.soup.find("body").findChildren(recursive=False)
        # except AttributeError:
        #     soup = self.soup.findChildren(recursive=False)
        # cached_fallback_value = (
        #     ""  # append fall back content here, by default it's a Rich Text block
        # )
        # cached_fallback_function = import_string(
        #     conf_fallback_block()
        # )  # Rich Text block
        soup = bs4(html, "html.parser")
        counter = 0
        for element in soup.findChildren(recursive=False):
            if element.name:
                counter += 1
                signature = make_tag_signature(element)
                print(signature)
        # for element in soup:  # each single top level tag
        #     counter += 1

        #     # the builder function for the element tag from config
        #     builder_function = self.get_builder_function(element)

        #     if builder_function:  # build a block
        #         if cached_fallback_value:
        #             cached_fallback_value = cached_fallback_function(
        #                 cached_fallback_value,
        #                 self.blocks,
        #             )  # before building a block write fall back cache to a block
        #         self.blocks.append(builder_function(element))
        #     else:
        #         if element.text.strip():  # exclude a tag that is empty
        #             cached_fallback_value += str(element)

        #     if cached_fallback_value and counter == len(
        #         soup
        #     ):  # the last tag so just build whats left in the fall back cache
        #         cached_fallback_value = cached_fallback_function(
        #             cached_fallback_value, self.blocks
        #         )

        # return self.blocks
