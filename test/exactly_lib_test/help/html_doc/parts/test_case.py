import unittest

from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.html_doc.parts import test_case as sut
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib_test.help.program_modes.test_case.test_resources import TEST_CASE_HELP_WITH_PRODUCTION_PHASES
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import is_target_info_node_list
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_document_structure(self):
        # ARRANGE #
        generator = sut.HtmlDocGeneratorForTestCaseHelp(TEST_CASE_HELP_WITH_PRODUCTION_PHASES, RENDERING_ENVIRONMENT)
        # ACT #
        targets, contents = generator.apply(CustomTargetInfoFactory('target-prefix'))
        # ASSERT #
        struct_check.is_section_contents.apply(self, contents)

    def test_target_info_hierarchy(self):
        # ARRANGE #
        generator = sut.HtmlDocGeneratorForTestCaseHelp(TEST_CASE_HELP_WITH_PRODUCTION_PHASES, RENDERING_ENVIRONMENT)
        # ACT #
        targets, contents = generator.apply(CustomTargetInfoFactory('target-prefix'))
        # ASSERT #
        is_target_info_node_list.apply(self, targets)


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
