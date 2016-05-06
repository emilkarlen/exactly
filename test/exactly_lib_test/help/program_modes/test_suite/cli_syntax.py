import unittest

from exactly_lib.help.program_modes.test_suite.contents.cli_syntax import SuiteCliSyntaxDocumentation
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ProgramDocumentationSectionContentsRenderer
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestCase(unittest.TestCase):
    def test(self):
        # ARRANGE #
        renderer = ProgramDocumentationSectionContentsRenderer(SuiteCliSyntaxDocumentation())
        cross_ref_text_constructor = CrossReferenceTextConstructorTestImpl()
        # ACT #
        actual = renderer.apply(RenderingEnvironment(cross_ref_text_constructor))
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)
