import unittest

from shellcheck_lib.execution import phases
from shellcheck_lib.help.program_modes.test_case.contents.main.overview import OverviewRenderer
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib_test.help.test_resources import test_case_phase_help, CrossReferenceTextConstructorTestImpl
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


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


TEST_CASE_HELP_WITH_PRODUCTION_PHASES = TestCaseHelp([
    test_case_phase_help(phases.ANONYMOUS.identifier, []),
    test_case_phase_help(phases.SETUP.identifier, []),
    test_case_phase_help(phases.ACT.identifier, []),
    test_case_phase_help(phases.BEFORE_ASSERT.identifier, []),
    test_case_phase_help(phases.ASSERT.identifier, []),
    test_case_phase_help(phases.CLEANUP.identifier, []),
])
