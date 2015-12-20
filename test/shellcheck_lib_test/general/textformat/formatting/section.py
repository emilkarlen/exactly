import unittest

from shellcheck_lib.general.textformat.formatting import section as sut
from shellcheck_lib.general.textformat.structure.document import SectionContents
from shellcheck_lib_test.general.textformat.formatting.test_resources import single_text_para


class TestSectionContents(unittest.TestCase):
    def test_only_single_initial_paragraph(self):
        formatter = sut.Formatter(page_width=100)
        actual = formatter.format_section_contents(SectionContents([single_text_para('paragraph')],
                                                                   []))
        self.assertEqual(['paragraph'],
                         actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestSectionContents))
    return ret_val


if __name__ == '__main__':
    unittest.main()
