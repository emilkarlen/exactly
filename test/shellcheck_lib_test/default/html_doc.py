import unittest

from shellcheck_lib.default.program_modes.test_case import default_instructions_setup
from shellcheck_lib.help.contents_structure import application_help_for
from shellcheck_lib.help.html import main as sut
from shellcheck_lib_test.test_resources.str_std_out_files import null_output_files


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestHtmlDoc))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestHtmlDoc(unittest.TestCase):
    def test_that_html_doc_generation_does_not_raise_an_exception(self):
        # ARRANGE #
        output = null_output_files()
        application_help = application_help_for(default_instructions_setup.INSTRUCTIONS_SETUP)
        generator = sut.HtmlDocGenerator(output, application_help)
        # ACT & ASSERT #
        generator.apply()
