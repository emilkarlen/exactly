from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout


def render(parent: Element,
           literal_layout: LiteralLayout) -> Element:
    """
    :return: The added element.
    """
    pre = SubElement(parent, 'pre')
    pre.text = literal_layout.literal_text
    return pre
