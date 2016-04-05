import io
import unittest
from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.util.textformat.formatting.html import document as sut
from shellcheck_lib.util.textformat.formatting.html.document import DOCTYPE_XHTML1_0
from shellcheck_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from shellcheck_lib.util.textformat.formatting.html.text import TextRenderer
from shellcheck_lib.util.textformat.structure.core import StringText
from shellcheck_lib.util.textformat.structure.document import SectionContents, Section
from shellcheck_lib.util.textformat.structure.structures import para
from shellcheck_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import TargetRendererTestImpl, \
    ParaWithSingleStrTextRenderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDocument),
        unittest.makeSuite(TestHeaderAndFooterPopulator),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestDocument(unittest.TestCase):
    def test_simple_document(self):
        # ARRANGE #
        section_contents = SectionContents(
            [para('para 0')],
            [Section(StringText('header 1'),
                     SectionContents([para('para 1'),
                                      para('')],
                                     []))])
        document_setup = sut.DocumentSetup('page title')
        # ACT #
        output_file = io.StringIO()
        DOCUMENT_RENDERER.apply(output_file, document_setup, section_contents)
        actual = output_file.getvalue()
        # ASSERT #
        expected = (DOCTYPE_XHTML1_0 +
                    '<html>'
                    '<head>'
                    '<title>page title</title>'
                    '</head>'
                    '<body>'
                    '<p>para 0</p>'
                    '<h1>header 1</h1>'
                    '<p>para 1</p>'
                    '<p />'
                    '</body>'
                    '</html>')
        self.assertEqual(expected,
                         actual)


class TestHeaderAndFooterPopulator(unittest.TestCase):
    def test_header_populator(self):
        # ARRANGE #
        section_contents = SectionContents(
            [para('main contents')],
            [])
        header_populator = SingleParaPopulator('header contents')
        document_setup = sut.DocumentSetup('page title',
                                           header_populator=header_populator)
        # ACT #
        output_file = io.StringIO()
        DOCUMENT_RENDERER.apply(output_file, document_setup, section_contents)
        actual = output_file.getvalue()
        # ASSERT #
        expected = (DOCTYPE_XHTML1_0 +
                    '<html>'
                    '<head>'
                    '<title>page title</title>'
                    '</head>'
                    '<body>'
                    '<p>header contents</p>'
                    '<p>main contents</p>'
                    '</body>'
                    '</html>')
        self.assertEqual(expected,
                         actual)

    def test_footer_populator(self):
        # ARRANGE #
        section_contents = SectionContents(
            [para('main contents')],
            [])
        footer_populator = SingleParaPopulator('footer contents')
        document_setup = sut.DocumentSetup('page title',
                                           footer_populator=footer_populator)
        # ACT #
        output_file = io.StringIO()
        DOCUMENT_RENDERER.apply(output_file, document_setup, section_contents)
        actual = output_file.getvalue()
        # ASSERT #
        expected = (DOCTYPE_XHTML1_0 +
                    '<html>'
                    '<head>'
                    '<title>page title</title>'
                    '</head>'
                    '<body>'
                    '<p>main contents</p>'
                    '<p>footer contents</p>'
                    '</body>'
                    '</html>')
        self.assertEqual(expected,
                         actual)

    def test_header_and_footer_populator(self):
        # ARRANGE #
        section_contents = SectionContents(
            [para('main contents')],
            [])
        header_populator = SingleParaPopulator('header contents')
        footer_populator = SingleParaPopulator('footer contents')
        document_setup = sut.DocumentSetup('page title',
                                           header_populator=header_populator,
                                           footer_populator=footer_populator)
        # ACT #
        output_file = io.StringIO()
        DOCUMENT_RENDERER.apply(output_file, document_setup, section_contents)
        actual = output_file.getvalue()
        # ASSERT #
        expected = (DOCTYPE_XHTML1_0 +
                    '<html>'
                    '<head>'
                    '<title>page title</title>'
                    '</head>'
                    '<body>'
                    '<p>header contents</p>'
                    '<p>main contents</p>'
                    '<p>footer contents</p>'
                    '</body>'
                    '</html>')
        self.assertEqual(expected,
                         actual)


class SingleParaPopulator(sut.ElementPopulator):
    def __init__(self, para_text: str):
        self.para_text = para_text

    def apply(self, parent: Element):
        SubElement(parent, 'p').text = self.para_text


TEST_SECTION_RENDERER = sut.SectionRenderer(HnSectionHeaderRenderer(TextRenderer(TargetRendererTestImpl())),
                                            ParaWithSingleStrTextRenderer())

DOCUMENT_RENDERER = sut.DocumentRenderer(TEST_SECTION_RENDERER)
