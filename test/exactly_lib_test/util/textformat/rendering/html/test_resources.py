import unittest
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, tostring

from exactly_lib.util.textformat.rendering.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.structure import core
from exactly_lib_test.test_resources.value_assertions import xml_etree as asrt_xml


def as_unicode_str(root: Element):
    return tostring(root, encoding="unicode")


def assert_contents_and_that_last_child_is_returned(
        expected: ET.Element,
        actual: Element,
        ret_val_from_renderer: Element,
        put: unittest.TestCase,
):
    assertion = asrt_xml.equals(expected)
    assertion.apply_with_message(
        put,
        actual,
        'XML',
    )
    put.assertIs(list(actual)[-1],
                 ret_val_from_renderer)


class CrossReferenceTargetTestImpl(core.CrossReferenceTarget):
    def __init__(self, name: str):
        self.name = name


class TargetRendererAsNameTestImpl(TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        assert isinstance(target, CrossReferenceTargetTestImpl)
        return target.name


TARGET_RENDERER_AS_NAME = TargetRendererAsNameTestImpl()
