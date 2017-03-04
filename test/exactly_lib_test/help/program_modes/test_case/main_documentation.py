import unittest

from exactly_lib.help.program_modes.test_case.contents.main import specification as sut
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
        rendering_environment = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
        # ACT #
        actual = sut.SpecificationRenderer(TEST_CASE_HELP_WITH_PRODUCTION_PHASES).apply(rendering_environment)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_target_info_hierarchy(self):
        # ARRANGE #
        overview_renderer = sut.SpecificationRenderer(TEST_CASE_HELP_WITH_PRODUCTION_PHASES)
        # ACT #
        actual = overview_renderer.target_info_hierarchy()
        # ASSERT #
        is_target_info_node_list.apply(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
