import unittest

from exactly_lib.help.program_modes.help import cli_syntax as sut
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib_test.util.textformat.construction.section_hierarchy.test_resources.misc import \
    CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


class TestCase(unittest.TestCase):
    def test(self):
        # ARRANGE #
        renderer = ProgramDocumentationSectionContentsConstructor(sut.HelpCliSyntaxDocumentation())
        cross_ref_text_constructor = CrossReferenceTextConstructorTestImpl()
        # ACT #
        actual = renderer.apply(ConstructionEnvironment(cross_ref_text_constructor))
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
