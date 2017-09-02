import io
import unittest

from exactly_lib.help.html_doc import main as sut
from exactly_lib.help.the_application_help import new_application_help
from exactly_lib.util.textformat.formatting.html.document import DOCTYPE_XHTML1_0
from exactly_lib_test.processing.test_resources.instruction_set import instruction_set
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import begins_with
from exactly_lib_test.test_suite.test_resources.configuration_section_instructions import \
    CONFIGURATION_SECTION_INSTRUCTIONS
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHtmlDoc)


class TestHtmlDoc(unittest.TestCase):
    TEST_CASE_INSTRUCTION_SET = instruction_set()
    TEST_SUITE_CONFIGURATION_SECTION_INSTRUCTIONS = CONFIGURATION_SECTION_INSTRUCTIONS

    def test_that_html_doc_renderer_returns_valid_section_contents(self):
        # ARRANGE #
        application_help = new_application_help(self.TEST_CASE_INSTRUCTION_SET,
                                                self.TEST_SUITE_CONFIGURATION_SECTION_INSTRUCTIONS)
        # ACT #
        actual = sut.section_contents(application_help)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_generate_and_output_SHOULD_output_xhtml(self):
        # ARRANGE #
        application_help = new_application_help(self.TEST_CASE_INSTRUCTION_SET,
                                                self.TEST_SUITE_CONFIGURATION_SECTION_INSTRUCTIONS)
        output_file = io.StringIO()
        # ACT #
        sut.generate_and_output(output_file, application_help)
        # ASSERT #
        actual_output = output_file.getvalue()
        begins_with(DOCTYPE_XHTML1_0).apply(self, actual_output, asrt.MessageBuilder('file output'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
