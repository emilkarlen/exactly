from xml.etree.ElementTree import Element, tostring


def as_unicode_str(root: Element):
    return tostring(root, encoding="unicode")
