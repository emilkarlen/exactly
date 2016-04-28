import unittest

from exactly_lib.execution import phases
from exactly_lib.help.program_modes.test_case.contents.main.overview import OverviewRenderer
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib_test.help.test_resources import test_case_phase_help, CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.utils.test_resources_.table_of_contents import is_target_info_hierarchy
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestCase(unittest.TestCase):
    def test_generate_overview_documentation(self):
        # ARRANGE #
        rendering_environment = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
        # ACT #
        actual = OverviewRenderer(TEST_CASE_HELP_WITH_PRODUCTION_PHASES).apply(rendering_environment)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_overview_documentation_target_info_hierarchy(self):
        # ARRANGE #
        overview_renderer = OverviewRenderer(TEST_CASE_HELP_WITH_PRODUCTION_PHASES)
        # ACT #
        actual = overview_renderer.target_info_hierarchy()
        # ASSERT #
        is_target_info_hierarchy.apply(self, actual)


TEST_CASE_HELP_WITH_PRODUCTION_PHASES = TestCaseHelp([
    test_case_phase_help(phases.CONFIGURATION.identifier, []),
    test_case_phase_help(phases.SETUP.identifier, []),
    test_case_phase_help(phases.ACT.identifier, []),
    test_case_phase_help(phases.BEFORE_ASSERT.identifier, []),
    test_case_phase_help(phases.ASSERT.identifier, []),
    test_case_phase_help(phases.CLEANUP.identifier, []),
])
