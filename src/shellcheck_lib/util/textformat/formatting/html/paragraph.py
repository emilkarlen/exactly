from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.util.textformat.formatting.html.text import TextRenderer, Position
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph


def render(text_renderer: TextRenderer,
           parent: Element,
           paragraph: Paragraph) -> Element:
    """
    :param para:
    :return: parent, if the paragraph is empty. Otherwise the added p element.
    """
    start_on_new_line_blocks = paragraph.start_on_new_line_blocks
    if not start_on_new_line_blocks:
        return parent
    p = SubElement(parent, 'p')

    text_renderer.apply(p, p, Position.INSIDE, start_on_new_line_blocks[0])
    for text in start_on_new_line_blocks[1:]:
        br = SubElement(p, 'br')
        text_renderer.apply(p, br, Position.AFTER, text)
    return p
