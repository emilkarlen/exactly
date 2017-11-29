import unittest
from xml.etree.ElementTree import Element, tostring

from exactly_lib.util.textformat.formatting.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.structure import core


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


class CrossReferenceTargetTestImpl(core.CrossReferenceTarget):
    def __init__(self, name: str):
        self.name = name


class TargetRendererAsNameTestImpl(TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        assert isinstance(target, CrossReferenceTargetTestImpl)
        return target.name


TARGET_RENDERER_AS_NAME = TargetRendererAsNameTestImpl()
