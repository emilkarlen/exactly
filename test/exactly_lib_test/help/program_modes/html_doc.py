import io
import unittest

from exactly_lib.help.contents_structure import application_help_for
from exactly_lib.help.html_doc import main as sut
from exactly_lib.util.textformat.formatting.html.document import DOCTYPE_XHTML1_0
from exactly_lib_test.processing.test_resources.instruction_set import instruction_set
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import begins_with
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHtmlDoc)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestHtmlDoc(unittest.TestCase):
    INSTRUCTION_SET = instruction_set()

    def test_that_html_doc_renderer_returns_valid_section_contents(self):
        # ARRANGE #
        application_help = application_help_for(self.INSTRUCTION_SET)
        renderer = sut.HtmlDocContentsRenderer(application_help)
        # ACT #
        actual = renderer.apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_generate_and_output_SHOULD_output_xhtml(self):
        # ARRANGE #
        application_help = application_help_for(self.INSTRUCTION_SET)
        output_file = io.StringIO()
        # ACT #
        sut.generate_and_output(output_file, application_help)
        # ASSERT #
        actual_output = output_file.getvalue()
        begins_with(DOCTYPE_XHTML1_0).apply(self, actual_output, va.MessageBuilder('file output'))
