import unittest
from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.formatting.html.paragraph_item import lists as sut
from exactly_lib.util.textformat.formatting.html.text import TextRenderer
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.structures import text, paras, para
from exactly_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import ConstantPRenderer
from exactly_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str, TargetRendererAsNameTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestItemizedListType),
        unittest.makeSuite(TestOrderedListType),
        unittest.makeSuite(TestVariableListType),
    ])


class TestItemizedListType(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([],
                                    lists.Format(lists.ListType.ITEMIZED_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root />',
                         xml_string)
        self.assertIs(root,
                      ret_val)

    def test_singleton_element_without_contents(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header')))],
                                    lists.Format(lists.ListType.ITEMIZED_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<ul><li>header</li></ul>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_multiple_element_without_contents(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header 1'))),
                                     lists.HeaderContentListItem(lists.HeaderItem(text('header 2')))],
                                    lists.Format(lists.ListType.ITEMIZED_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<ul>'
                         '<li>header 1</li>'
                         '<li>header 2</li>'
                         '</ul>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_element_with_single_para_contents(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header')),
                                                                 paras('ignored'))],
                                    lists.Format(lists.ListType.ITEMIZED_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('every para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<ul>'
                         '<li>header<p>every para text</p></li>'
                         '</ul>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_element_with_multiple_para_contents(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header')),
                                                                 [para('ignored'),
                                                                  para('ignored')])],
                                    lists.Format(lists.ListType.ITEMIZED_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('every para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<ul>'
                         '<li>header'
                         '<p>every para text</p>'
                         '<p>every para text</p>'
                         '</li>'
                         '</ul>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


class TestOrderedListType(unittest.TestCase):
    def test_singleton_element_without_contents(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header')))],
                                    lists.Format(lists.ListType.ORDERED_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<ol>'
                         '<li>header</li>'
                         '</ol>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


class TestVariableListType(unittest.TestCase):
    def test_singleton_element_without_contents(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header')))],
                                    lists.Format(lists.ListType.VARIABLE_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<dl>'
                         '<dt>header</dt>'
                         '</dl>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_singleton_element_with_multiple_content_paragraphs(self):
        # ARRANGE #
        root = Element('root')
        l = lists.HeaderContentList([lists.HeaderContentListItem(lists.HeaderItem(text('header')),
                                                                 [para('ignored'),
                                                                  para('ignored')])],
                                    lists.Format(lists.ListType.VARIABLE_LIST))
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER),
                             ConstantPRenderer('para text'),
                             root, l)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<dl>'
                         '<dt>header</dt>'
                         '<dd>'
                         '<p>para text</p>'
                         '<p>para text</p>'
                         '</dd>'
                         '</dl>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


TARGET_RENDERER = TargetRendererAsNameTestImpl()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
