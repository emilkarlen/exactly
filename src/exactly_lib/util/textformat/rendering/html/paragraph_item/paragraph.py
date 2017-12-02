from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.rendering.html.text import TextRenderer, Position
from exactly_lib.util.textformat.structure.paragraph import Paragraph


def render(text_renderer: TextRenderer,
           parent: Element,
           paragraph: Paragraph,
           skip_surrounding_p_element=False) -> Element:
    """
    :param para:
    :return: parent, if the paragraph is empty. Otherwise the added p element.
    """
    start_on_new_line_blocks = paragraph.start_on_new_line_blocks
    if not start_on_new_line_blocks:
        return parent
    if skip_surrounding_p_element:
        element_container = parent
    else:
        element_container = SubElement(parent, 'p')

    text_renderer.apply(element_container, element_container, Position.INSIDE,
                        start_on_new_line_blocks[0])
    for text in start_on_new_line_blocks[1:]:
        br = SubElement(element_container, 'br')
        text_renderer.apply(element_container, br, Position.AFTER, text)
    return element_container
