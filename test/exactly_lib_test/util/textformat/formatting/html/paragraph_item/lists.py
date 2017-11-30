import unittest
from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.formatting.html.paragraph_item import lists as sut
from exactly_lib.util.textformat.formatting.html.text import TextRenderer
from exactly_lib.util.textformat.structure.lists import HeaderContentListItem, Format, HeaderContentList, ListType, \
    HeaderItem
from exactly_lib.util.textformat.structure.structures import text, paras, para
from exactly_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import ConstantPRenderer
from exactly_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str, TargetRendererAsNameTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEmpty),
        unittest.makeSuite(TestItemizedAndOrderedListType),
        unittest.makeSuite(TestVariableListType),
    ])


class Case:
    def __init__(self,
                 name: str,
                 items: list,
                 expected: str):
        self.name = name
        self.items = items
        self.expected = expected


class TestEmpty(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        for list_type in ListType:
            with self.subTest(list_type=list_type):
                root = Element('root')
                the_list = HeaderContentList([],
                                             Format(list_type))
                # ACT #
                ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                                     ConstantPRenderer('para text'),
                                     root, the_list)
                # ASSERT #
                xml_string = as_unicode_str(root)
                self.assertEqual('<root />',
                                 xml_string)
                self.assertIs(root,
                              ret_val)


class TestItemizedAndOrderedListType(unittest.TestCase):
    def test_non_empty(self):
        # ARRANGE #
        cases = [
            Case('test_singleton_element_without_contents',
                 items=
                 [HeaderContentListItem(HeaderItem(text('header')))],
                 expected=
                 '<root>'
                 '<{L}><li>header</li></{L}>'
                 '</root>',
                 ),
            Case('test_multiple_element_without_contents',
                 items=
                 [HeaderContentListItem(HeaderItem(text('header 1'))),
                  HeaderContentListItem(HeaderItem(text('header 2')))],
                 expected=
                 '<root>'
                 '<{L}>'
                 '<li>header 1</li>'
                 '<li>header 2</li>'
                 '</{L}>'
                 '</root>',
                 ),
            Case('test_single_element_with_single_para_contents',
                 items=
                 [HeaderContentListItem(HeaderItem(text('header')),
                                        paras('ignored'))],
                 expected=
                 '<root>'
                 '<{L}>'
                 '<li>header<p>every para text</p></li>'
                 '</{L}>'
                 '</root>',
                 ),
            Case('test_single_element_with_multiple_para_contents',
                 items=
                 [HeaderContentListItem(HeaderItem(text('header')),
                                        [para('ignored'),
                                         para('ignored')])],
                 expected=
                 '<root>'
                 '<{L}>'
                 '<li>header'
                 '<p>every para text</p>'
                 '<p>every para text</p>'
                 '</li>'
                 '</{L}>'
                 '</root>',
                 ),
        ]
        for list_type, element in [(ListType.ITEMIZED_LIST, 'ul'),
                                   (ListType.ORDERED_LIST, 'ol')]:
            for case in cases:
                with self.subTest(list_type=list_type, case=case.name):
                    root = Element('root')
                    the_list = HeaderContentList(case.items, Format(list_type))
                    # ACT #
                    ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                                         ConstantPRenderer('every para text'),
                                         root, the_list)
                    # ASSERT #
                    expected = case.expected.format(L=element)
                    xml_string = as_unicode_str(root)
                    self.assertEqual(expected,
                                     xml_string)
                    self.assertIs(list(root)[0],
                                  ret_val)


class TestVariableListType(unittest.TestCase):
    def test(self):
        cases = [
            Case(
                'test_singleton_element_without_contents',
                items=
                [HeaderContentListItem(HeaderItem(text('header')))],
                expected=
                '<root>'
                '<dl>'
                '<dt>header</dt>'
                '</dl>'
                '</root>'
            ),
            Case(
                'test_singleton_element_with_multiple_content_paragraphs',
                items=
                [HeaderContentListItem(HeaderItem(text('header')),
                                       [para('ignored'),
                                        para('ignored')])],
                expected=
                '<root>'
                '<dl>'
                '<dt>header</dt>'
                '<dd>'
                '<p>every para text</p>'
                '<p>every para text</p>'
                '</dd>'
                '</dl>'
                '</root>'
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                root = Element('root')
                the_list = HeaderContentList(case.items, Format(ListType.VARIABLE_LIST))
                # ACT #
                ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                                     ConstantPRenderer('every para text'),
                                     root, the_list)
                # ASSERT #
                xml_string = as_unicode_str(root)
                self.assertEqual(case.expected,
                                 xml_string)
                self.assertIs(list(root)[0],
                              ret_val)


TARGET_RENDERER = TargetRendererAsNameTestImpl()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
