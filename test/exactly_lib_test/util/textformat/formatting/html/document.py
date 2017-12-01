import io
import unittest
from xml.etree.ElementTree import Element, SubElement

from exactly_lib.util.textformat.formatting.html import document as sut
from exactly_lib.util.textformat.formatting.html import utils
from exactly_lib.util.textformat.formatting.html.document import DOCTYPE_XHTML1_0
from exactly_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.formatting.html.text import TextRenderer
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.document import SectionContents, Section
from exactly_lib.util.textformat.structure.structures import para
from exactly_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import ParaWithSingleStrTextRenderer
from exactly_lib_test.util.textformat.formatting.html.test_resources import TARGET_RENDERER_AS_NAME


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDocument),
        unittest.makeSuite(TestHeaderAndFooterPopulator),
        unittest.makeSuite(TestHeadPopulator),
        unittest.makeSuite(TestComplexElementPopulator),
    ])


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

                    '<section>'

                    '<header>'
                    '<h1>header 1</h1>'
                    '</header>'

                    '<p>para 1</p>'
                    '<p />'
                    '</section>'
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


class TestHeadPopulator(unittest.TestCase):
    def test_header_populator(self):
        # ARRANGE #
        section_contents = SectionContents(
            [para('main contents')],
            [])
        head_populator = HeadStylePopulator('p {color:blue;}')
        document_setup = sut.DocumentSetup('page title',
                                           head_populator=head_populator)
        # ACT #
        output_file = io.StringIO()
        DOCUMENT_RENDERER.apply(output_file, document_setup, section_contents)
        actual = output_file.getvalue()
        # ASSERT #
        expected = (DOCTYPE_XHTML1_0 +
                    '<html>'
                    '<head>'
                    '<title>page title</title>'
                    '<style>p {color:blue;}</style>'
                    '</head>'
                    '<body>'
                    '<p>main contents</p>'
                    '</body>'
                    '</html>')
        self.assertEqual(expected,
                         actual)


class TestComplexElementPopulator(unittest.TestCase):
    def test_simple_document(self):
        # ARRANGE #
        section_contents = SectionContents(
            [para('para in contents')],
            [])
        populator = utils.ComplexElementPopulator([SingleParaPopulator('para from pop 1'),
                                                   SingleParaPopulator('para from pop 2')])
        document_setup = sut.DocumentSetup('page title',
                                           footer_populator=populator)
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

                    '<p>para in contents</p>'

                    '<p>para from pop 1</p>'
                    '<p>para from pop 2</p>'

                    '</body>'
                    '</html>')
        self.assertEqual(expected,
                         actual)


class SingleParaPopulator(utils.ElementPopulator):
    def __init__(self, para_text: str):
        self.para_text = para_text

    def apply(self, parent: Element):
        SubElement(parent, 'p').text = self.para_text


class HeadStylePopulator(utils.ElementPopulator):
    def __init__(self, style: str):
        self.style = style

    def apply(self, parent: Element):
        SubElement(parent, 'style').text = self.style


TEST_SECTION_RENDERER = sut.SectionItemRenderer(TARGET_RENDERER_AS_NAME,
                                                HnSectionHeaderRenderer(TextRenderer(TARGET_RENDERER_AS_NAME)),
                                                ParaWithSingleStrTextRenderer())

DOCUMENT_RENDERER = sut.DocumentRenderer(TEST_SECTION_RENDERER)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
