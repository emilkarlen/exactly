import unittest
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from exactly_lib.util.textformat.formatting.html import text as sut
from exactly_lib.util.textformat.formatting.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import StringText, CrossReferenceText, CrossReferenceTarget, Text, \
    AnchorText
from exactly_lib_test.util.textformat.formatting.html.test_resources import \
    assert_contents_and_that_last_child_is_returned, as_unicode_str


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Case:
    def __init__(self,
                 name: str,
                 text: Text,
                 expected: str):
        self.name = name
        self.text = text
        self.expected = expected


_CONSTANT_TARGET_STR = 'constant-target'


def _test_inside(put: unittest.TestCase, case: Case):
    renderer = sut.TextRenderer(_ConstantTargetRenderer(_CONSTANT_TARGET_STR))
    root = Element('root')
    # ACT #
    actual = renderer.apply(root, root, sut.Position.INSIDE, case.text)
    # ASSERT #
    expected_xml = '<root>{}</root>'.format(case.expected)
    assert_contents_and_that_last_child_is_returned(
        expected_xml,
        root,
        actual,
        put)


def _test_after(put: unittest.TestCase, case: Case):
    renderer = sut.TextRenderer(_ConstantTargetRenderer(_CONSTANT_TARGET_STR))
    root = Element('root')
    sub = SubElement(root, 'sub')
    # ACT #
    actual = renderer.apply(root, sub, sut.Position.AFTER, case.text)
    # ASSERT #
    expected_xml = '<root><sub />{}</root>'.format(case.expected)
    assert_contents_and_that_last_child_is_returned(
        expected_xml,
        root,
        actual,
        put)


def _cases(put: unittest.TestCase, cases: list):
    for case in cases:
        for position in sut.Position:
            with put.subTest(case=case.name, position=position):
                if position is position.INSIDE:
                    _test_inside(put, case)
                else:
                    _test_after(put, case)


class Test(unittest.TestCase):
    def test_string_text__inside(self):
        # ARRANGE #

        renderer = sut.TextRenderer(TargetRenderer())
        root = Element('root')
        source_text = 'source text'
        text = StringText(source_text)

        # ACT #

        actual = renderer.apply(root, root, sut.Position.INSIDE, text)

        # ASSERT #

        expected_xml = '<root>{}</root>'.format(source_text)
        actual_xml = as_unicode_str(root)
        self.assertEqual(source_text, actual.text)
        self.assertEqual(expected_xml,
                         actual_xml)

        self.assertIs(root, actual, 'Returned Element')

    def test_string_text__after(self):
        # ARRANGE #

        renderer = sut.TextRenderer(TargetRenderer())
        root = Element('root')
        sub = SubElement(root, 'sub')
        source_text = 'source text'
        text = StringText(source_text)

        # ACT #

        actual = renderer.apply(root, sub, sut.Position.AFTER, text)

        # ASSERT #
        self.assertEqual(source_text, sub.tail)
        expected_xml = '<root><sub />{}</root>'.format(source_text)
        actual_xml = as_unicode_str(root)
        self.assertEqual(expected_xml,
                         actual_xml)

        self.assertIs(root, actual, 'Returned Element')

    def test_cross_reference(self):
        _cases(self,
               [
                   Case('target in same doc',
                        text=CrossReferenceText('title text',
                                                CrossReferenceTarget())
                        ,
                        expected='<a href="#{target_name}">title text</a>'.format(target_name=_CONSTANT_TARGET_STR),
                        ),
                   Case('target in other doc',
                        text=CrossReferenceText('title text',
                                                CrossReferenceTarget(),
                                                target_is_id_in_same_document=False)
                        ,
                        expected='<a href="{target_name}">title text</a>'.format(target_name=_CONSTANT_TARGET_STR),
                        ),
               ])

    def test_anchor(self):
        _cases(self,
               [
                   Case('anchor',
                        text=AnchorText(StringText('anchor text'),
                                        CrossReferenceTarget())
                        ,
                        expected='<span id="{target_name}">anchor text</span>'.format(target_name=_CONSTANT_TARGET_STR),
                        ),
               ])


class _ConstantTargetRenderer(TargetRenderer):
    def __init__(self, target_str: str):
        self.target_str = target_str

    def apply(self, target: core.CrossReferenceTarget) -> str:
        return self.target_str
