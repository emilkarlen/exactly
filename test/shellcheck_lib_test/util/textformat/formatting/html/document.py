import io
import unittest

from shellcheck_lib.util.textformat.formatting.html import document as sut
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
        expected = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
                    '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
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


TEST_SECTION_RENDERER = sut.SectionRenderer(HnSectionHeaderRenderer(TextRenderer(TargetRendererTestImpl())),
                                            ParaWithSingleStrTextRenderer())

DOCUMENT_RENDERER = sut.DocumentRenderer(TEST_SECTION_RENDERER)
