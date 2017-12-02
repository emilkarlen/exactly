from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.rendering.html import text
from exactly_lib.util.textformat.rendering.html.paragraph_item.interfaces import ParagraphItemRenderer
from exactly_lib.util.textformat.rendering.html.text import Position
from exactly_lib.util.textformat.structure import lists


def render(text_renderer: text.TextRenderer,
           paragraph_item_renderer: ParagraphItemRenderer,
           parent: Element,
           list_: lists.HeaderContentList) -> Element:
    """
    :return: The added element.
    """
    if not list_.items:
        return parent
    if list_.list_format.list_type is not lists.ListType.VARIABLE_LIST:
        return _render_standard_list(text_renderer, paragraph_item_renderer, parent, list_)
    else:
        return _render_definition_list(text_renderer, paragraph_item_renderer, parent, list_)


def _render_standard_list(text_renderer: text.TextRenderer,
                          paragraph_item_renderer: ParagraphItemRenderer,
                          parent: Element,
                          list_: lists.HeaderContentList) -> Element:
    """
    :return: The added element.
    """
    list_root = list_element_for(parent, list_.list_format)
    for item in list_.items:
        li = SubElement(list_root, 'li')
        text_renderer.apply(li, li, Position.INSIDE, item.header)
        for paragraph_item in item.content_paragraph_items:
            paragraph_item_renderer.apply(li, paragraph_item)
    return list_root


def _render_definition_list(text_renderer: text.TextRenderer,
                            paragraph_item_renderer: ParagraphItemRenderer,
                            parent: Element,
                            list_: lists.HeaderContentList) -> Element:
    """
    :return: The added element.
    """
    list_root = SubElement(parent, 'dl')
    for item in list_.items:
        assert isinstance(item, lists.HeaderContentListItem)  # Type info for IDE
        dt = SubElement(list_root, 'dt', )
        text_renderer.apply(dt, dt, Position.INSIDE, item.header)
        content_paragraph_items = item.content_paragraph_items
        if content_paragraph_items:
            dd = SubElement(list_root, 'dd')
            for paragraph_item in content_paragraph_items:
                paragraph_item_renderer.apply(dd, paragraph_item)
    return list_root


def list_element_for(parent: Element, list_format: lists.Format) -> Element:
    list_type = list_format.list_type
    if list_type is lists.ListType.ITEMIZED_LIST:
        tag = 'ul'
    elif list_type is lists.ListType.ORDERED_LIST:
        tag = 'ol'
    else:
        raise ValueError('Unknown %s: %s' % (str(lists.ListType), str(list_type)))
    return SubElement(parent, tag)
