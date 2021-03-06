import unittest

from exactly_lib.help.program_modes.test_case.contents.cli_syntax import TestCaseCliSyntaxDocumentation
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib_test.util.textformat.constructor.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


class TestCase(unittest.TestCase):
    def test(self):
        # ARRANGE #
        constructor = ProgramDocumentationSectionContentsConstructor(TestCaseCliSyntaxDocumentation())
        cross_ref_text_constructor = CrossReferenceTextConstructorTestImpl()
        # ACT #
        actual = constructor.apply(ConstructionEnvironment(cross_ref_text_constructor))
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
