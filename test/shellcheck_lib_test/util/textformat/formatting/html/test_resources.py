import unittest
from xml.etree.ElementTree import Element, tostring


def as_unicode_str(root: Element):
    return tostring(root, encoding="unicode")


def assert_contents_and_that_last_child_is_returned(
        expected_xml: str,
        root: Element,
        ret_val_from_renderer: Element,
        put: unittest.TestCase):
    xml_string = as_unicode_str(root)
    put.assertEqual(expected_xml,
                    xml_string)
    put.assertIs(list(root)[-1],
                 ret_val_from_renderer)
