import unittest
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from exactly_lib.util.textformat.rendering.html import text as sut
from exactly_lib.util.textformat.rendering.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import StringText, CrossReferenceText, CrossReferenceTarget, Text, \
    AnchorText
from exactly_lib_test.util.textformat.rendering.html.test_resources import \
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


def _cases(put: unittest.TestCase, cases: list):
    for case in cases:
        for position in sut.Position:
            with put.subTest(case=case.name, position=position):
                if position is position.INSIDE:
                    _test_inside(put, case)
                else:
                    _test_after(put, case)


class Test(unittest.TestCase):
    def test_plain_string_text__inside(self):
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

    def test_plain_string_text__after(self):
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

    def test_string_with_tags(self):
        _cases(self,
               [
                   Case('tags',
                        text=StringText('the text', tags={'1st', '2nd'}),
                        expected='<span class="1st 2nd">the text</span>',
                        ),
               ])

    def test_cross_reference(self):
        _cases(self,
               [
                   Case('target in same doc',
                        text=CrossReferenceText(StringText('title text'),
                                                _CrossReferenceString('the-target'))
                        ,
                        expected='<a href="#the-target">title text</a>',
                        ),
                   Case('target in other doc',
                        text=CrossReferenceText(StringText('title text'),
                                                _CrossReferenceString('the-target'),
                                                target_is_id_in_same_document=False)
                        ,
                        expected='<a href="the-target">title text</a>',
                        ),
                   Case('with tags',
                        text=CrossReferenceText(StringText('title text'),
                                                _CrossReferenceString('the-target'),
                                                tags={'1st', '2nd'})
                        ,
                        expected='<a class="1st 2nd" href="#the-target">title text</a>',
                        ),
               ])

    def test_anchor(self):
        _cases(self,
               [
                   Case('anchor without tagged content',
                        text=AnchorText(StringText('anchor text'),
                                        _CrossReferenceString('the-target'))
                        ,
                        expected='<span id="the-target">anchor text</span>',
                        ),
                   Case('anchor with tagged string text',
                        text=AnchorText(StringText('anchor text', tags={'1st', '2nd'}),
                                        _CrossReferenceString('the-target'))
                        ,
                        expected='<span id="the-target">'
                                 '<span class="1st 2nd">'
                                 'anchor text'
                                 '</span>'
                                 '</span>',
                        ),
                   Case('anchor with tagged cross-ref text',
                        text=AnchorText(CrossReferenceText(StringText('title text'),
                                                           _CrossReferenceString('target-of-anchored'),
                                                           tags={'tag1', 'tag2'}),
                                        _CrossReferenceString('target-of-anchor'))
                        ,
                        expected='<span id="target-of-anchor">'
                                 '<a class="tag1 tag2" href="#target-of-anchored">title text</a>'
                                 '</span>',
                        ),
               ])


class _CrossReferenceString(CrossReferenceTarget):
    def __init__(self, string: str):
        self.string = string


class _StringTargetRenderer(TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        assert isinstance(target, _CrossReferenceString)
        return target.string


def _test_inside(put: unittest.TestCase, case: Case):
    renderer = sut.TextRenderer(_StringTargetRenderer())
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
    renderer = sut.TextRenderer(_StringTargetRenderer())
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
