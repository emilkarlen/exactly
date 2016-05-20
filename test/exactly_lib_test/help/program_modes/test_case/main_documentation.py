import unittest

from exactly_lib.execution import phases
from exactly_lib.help.program_modes.test_case.contents.main.specification import SpecificationRenderer
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib_test.help.test_resources import section_documentation, CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import is_target_info_hierarchy
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestCase(unittest.TestCase):
    def test_generate_overview_documentation(self):
        # ARRANGE #
        rendering_environment = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
        # ACT #
        actual = SpecificationRenderer(TEST_CASE_HELP_WITH_PRODUCTION_PHASES).apply(rendering_environment)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_overview_documentation_target_info_hierarchy(self):
        # ARRANGE #
        overview_renderer = SpecificationRenderer(TEST_CASE_HELP_WITH_PRODUCTION_PHASES)
        # ACT #
        actual = overview_renderer.target_info_hierarchy()
        # ASSERT #
        is_target_info_hierarchy.apply(self, actual)


TEST_CASE_HELP_WITH_PRODUCTION_PHASES = TestCaseHelp([
    section_documentation(phases.CONFIGURATION.identifier, []),
    section_documentation(phases.SETUP.identifier, []),
    section_documentation(phases.ACT.identifier, []),
    section_documentation(phases.BEFORE_ASSERT.identifier, []),
    section_documentation(phases.ASSERT.identifier, []),
    section_documentation(phases.CLEANUP.identifier, []),
])
