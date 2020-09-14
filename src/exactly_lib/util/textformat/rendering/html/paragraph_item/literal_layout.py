from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout


def render(parent: Element,
           literal_layout: LiteralLayout) -> Element:
    """
    :return: The added element.
    """
    attributes = (
        dict()
        if literal_layout.class_ is None
        else
        {'class': literal_layout.class_}
    )
    pre = SubElement(parent, 'pre', attrib=attributes)
    pre.text = literal_layout.literal_text
    return pre
