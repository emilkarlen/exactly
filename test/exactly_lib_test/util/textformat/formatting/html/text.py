import unittest
from xml.etree.ElementTree import Element, tostring
from xml.etree.ElementTree import SubElement

from exactly_lib.util.textformat.formatting.html import text as sut
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import StringText, CrossReferenceText, CrossReferenceTarget
from exactly_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str, \
    assert_contents_and_that_last_child_is_returned


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_string_text__inside(self):
        # ARRANGE #
        renderer = sut.TextRenderer(sut.TargetRenderer())
        root = Element('root')
        source_text = 'source text'
        text = StringText(source_text)
        # ACT #
        actual = renderer.apply(root, root, sut.Position.INSIDE, text)
        # ASSERT #
        expected_html = '<root>{}</root>'.format(source_text)
        actual_html = tostring(root, encoding='unicode')
        self.assertEquals(source_text, actual.text)
        self.assertEquals(expected_html,
                          actual_html)

        self.assertIs(root, actual, 'Returned Element')

    def test_string_text__after(self):
        # ARRANGE #
        renderer = sut.TextRenderer(sut.TargetRenderer())
        root = Element('root')
        sub = SubElement(root, 'sub')
        source_text = 'source text'
        text = StringText(source_text)
        # ACT #
        actual = renderer.apply(root, sub, sut.Position.AFTER, text)
        # ASSERT #
        self.assertEquals(source_text, sub.tail)
        s = as_unicode_str(root)

        self.assertIs(root, actual, 'Returned Element')

    def test_cross_reference_text__inside(self):
        # ARRANGE #
        target_str = 'target-name'
        renderer = sut.TextRenderer(_ConstantTargetRenderer(target_str))
        root = Element('root')
        title_text = 'source text'
        text = CrossReferenceText(title_text,
                                  CrossReferenceTarget())
        # ACT #
        actual = renderer.apply(root, root, sut.Position.INSIDE, text)
        # ASSERT #
        expected_html = ('<root>'
                         '<a href="#{target_name}">{title_text}</a>'
                         '</root>'.format(title_text=title_text, target_name=target_str)
                         )
        assert_contents_and_that_last_child_is_returned(
            expected_html,
            root,
            actual,
            self)

    def test_cross_reference_text__target_is_not_in_same_document(self):
        # ARRANGE #
        target_str = 'target-name'
        renderer = sut.TextRenderer(_ConstantTargetRenderer(target_str))
        root = Element('root')
        title_text = 'source text'
        text = CrossReferenceText(title_text,
                                  CrossReferenceTarget(),
                                  target_is_id_in_same_document=False)
        # ACT #
        actual = renderer.apply(root, root, sut.Position.INSIDE, text)
        # ASSERT #
        expected_html = ('<root>'
                         '<a href="{target_name}">{title_text}</a>'
                         '</root>'.format(title_text=title_text, target_name=target_str)
                         )
        assert_contents_and_that_last_child_is_returned(
            expected_html,
            root,
            actual,
            self)


class _ConstantTargetRenderer(sut.TargetRenderer):
    def __init__(self, target_str: str):
        self.target_str = target_str

    def apply(self, target: core.CrossReferenceTarget) -> str:
        return self.target_str
