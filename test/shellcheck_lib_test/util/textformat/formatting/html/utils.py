import unittest
from xml.etree.ElementTree import Element, SubElement

import shellcheck_lib.util.textformat.formatting.html.utils
from shellcheck_lib.util.textformat.formatting.html import utils as sut
from shellcheck_lib.util.textformat.formatting.html.text import TextRenderer
from shellcheck_lib.util.textformat.structure.structures import para
from shellcheck_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestComplexElementPopulator),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestComplexElementPopulator(unittest.TestCase):
    def test_simple_document(self):
        # ARRANGE #
        root = Element('root')
        complex_populator = sut.ComplexElementPopulator([
            SingleParaPopulator('first'),
            SingleParaPopulator('second'),
        ])
        # ACT #
        complex_populator.apply(root)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>first</p>'
                         '<p>second</p>'
                         '</root>',
                         xml_string)


class SingleParaPopulator(shellcheck_lib.util.textformat.formatting.html.utils.ElementPopulator):
    def __init__(self, para_text: str):
        self.para_text = para_text

    def apply(self, parent: Element):
        SubElement(parent, 'p').text = self.para_text
