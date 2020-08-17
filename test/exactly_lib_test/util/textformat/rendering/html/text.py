import unittest
from typing import List
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from exactly_lib.util.textformat.rendering.html import text as sut
from exactly_lib.util.textformat.rendering.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import StringText, CrossReferenceText, CrossReferenceTarget, Text, \
    AnchorText
from exactly_lib_test.test_resources.value_assertions import xml_etree as asrt_xml
from exactly_lib_test.test_resources.xml_etree import element
from exactly_lib_test.util.textformat.rendering.html.test_resources import \
    assert_contents_and_that_last_child_is_returned


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Case:
    def __init__(self,
                 name: str,
                 text: Text,
                 expected: ET.Element):
        self.name = name
        self.text = text
        self.expected = expected


def _cases(put: unittest.TestCase, cases: List[Case]):
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

        root_tag_name = 'root'
        source_text = 'source text'

        root_element_to_mutate = Element(root_tag_name)

        renderer = sut.TextRenderer(TargetRenderer())
        text = StringText(source_text)

        # EXPECTATION #

        expected_element = element(root_tag_name, text=source_text)
        assertion = asrt_xml.equals(expected_element)

        # ACT #

        actual = renderer.apply(root_element_to_mutate, root_element_to_mutate, sut.Position.INSIDE, text)

        # ASSERT #

        assertion.apply_with_message(self, actual, 'element structure')
        self.assertIs(root_element_to_mutate, actual, 'returned element object')

    def test_plain_string_text__after(self):
        # ARRANGE #

        root_tag_name = 'root'
        source_text = 'source text'

        root_element_to_mutate = Element(root_tag_name)
        sub = SubElement(root_element_to_mutate, 'sub')

        renderer = sut.TextRenderer(TargetRenderer())
        text = StringText(source_text)

        # EXPECTATION #

        expected_element = element(root_tag_name,
                                   children=[element(sub.tag, tail=source_text)])
        assertion = asrt_xml.equals(expected_element)

        # ACT #

        actual = renderer.apply(root_element_to_mutate, sub, sut.Position.AFTER, text)

        # ASSERT #
        assertion.apply_with_message(self, actual, 'element structure')
        self.assertIs(root_element_to_mutate, actual, 'returned element object')

    def test_string_with_tags(self):
        _cases(self,
               [
                   Case('tags',
                        text=StringText('the text', tags={'1st', '2nd'}),
                        expected=element('span',
                                         attributes={'class': '1st 2nd'},
                                         text='the text')
                        ),
               ])

    def test_cross_reference(self):
        _cases(self,
               [
                   Case('target in same doc',
                        text=CrossReferenceText(StringText('title text'),
                                                _CrossReferenceString('the-target'))
                        ,
                        expected=element('a',
                                         attributes={'href': '#the-target'},
                                         text='title text'),
                        ),
                   Case('target in other doc',
                        text=CrossReferenceText(StringText('title text'),
                                                _CrossReferenceString('the-target'),
                                                target_is_id_in_same_document=False)
                        ,
                        expected=element('a',
                                         attributes={'href': 'the-target'},
                                         text='title text'),
                        ),
                   Case('with tags',
                        text=CrossReferenceText(StringText('title text'),
                                                _CrossReferenceString('the-target'),
                                                tags={'1st', '2nd'})
                        ,
                        expected=element('a',
                                         attributes={'href': '#the-target',
                                                     'class': '1st 2nd'},
                                         text='title text'),
                        ),
               ])

    def test_anchor(self):
        _cases(self,
               [
                   Case('anchor without tagged content',
                        text=AnchorText(StringText('anchor text'),
                                        _CrossReferenceString('the-target'))
                        ,
                        expected=element('span',
                                         attributes={'id': "the-target"},
                                         text='anchor text'),
                        ),
                   Case('anchor with tagged string text',
                        text=AnchorText(StringText('anchor text', tags={'1st', '2nd'}),
                                        _CrossReferenceString('the-target'))
                        ,
                        expected=element('span',
                                         attributes={'id': 'the-target'},
                                         children=[
                                             element('span', attributes={'class': '1st 2nd'}, text='anchor text')
                                         ]),
                        ),
                   Case('anchor with tagged cross-ref text',
                        text=AnchorText(CrossReferenceText(StringText('title text'),
                                                           _CrossReferenceString('target-of-anchored'),
                                                           tags={'tag1', 'tag2'}),
                                        _CrossReferenceString('target-of-anchor'))
                        ,
                        expected=element('span',
                                         attributes={'id': "target-of-anchor"},
                                         children=[element('a',
                                                           attributes={'class': "tag1 tag2",
                                                                       'href': "#target-of-anchored"},
                                                           text='title text',
                                                           )])
                        ,
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
    # ARRANGE #
    root_element_to_mutate = Element('root')

    renderer = sut.TextRenderer(_StringTargetRenderer())
    # ACT #
    actual = renderer.apply(root_element_to_mutate, root_element_to_mutate, sut.Position.INSIDE, case.text)
    # ASSERT #
    expected_xml = element('root', children=[case.expected])
    assert_contents_and_that_last_child_is_returned(
        expected_xml,
        root_element_to_mutate,
        actual,
        put)


def _test_after(put: unittest.TestCase, case: Case):
    root_element_to_mutate = Element('root')
    sub = SubElement(root_element_to_mutate, 'sub')

    renderer = sut.TextRenderer(_StringTargetRenderer())
    # ACT #
    actual = renderer.apply(root_element_to_mutate, sub, sut.Position.AFTER, case.text)
    # ASSERT #
    expected_xml = element('root',
                           children=[element('sub'), case.expected])
    assert_contents_and_that_last_child_is_returned(
        expected_xml,
        root_element_to_mutate,
        actual,
        put)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
