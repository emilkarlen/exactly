import unittest

from shellcheck_lib.help.program_modes.test_case.contents_structure import \
    TestCasePhaseInstructionSet, TestCasePhaseHelpForPhaseWithoutInstructions, TestCasePhaseHelpForPhaseWithInstructions
from shellcheck_lib.help.program_modes.test_case.render import test_case_phase as sut
from shellcheck_lib.help.utils.description import single_line_description, Description
from shellcheck_lib.util.textformat.structure.paragraph import para
from shellcheck_lib_test.help.test_resources import test_case_phase_instruction_set
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


class TestRenderHelpSansInstructions(unittest.TestCase):
    def test_description_sans_rest_part(self):
        # ARRANGE
        tcp_help = TestCasePhaseHelpForPhaseWithoutInstructions(
            'phase name',
            single_line_description('single line description'))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_description_with_rest_part(self):
        # ARRANGE
        tcp_help = TestCasePhaseHelpForPhaseWithoutInstructions(
            'phase name',
            Description('single line description',
                        [para('rest part para 1'),
                         para('rest part para 2')]))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)


class TestRenderHelpWithInstructions(unittest.TestCase):
    def test_description_sans_rest_part(self):
        # ARRANGE
        tcp_help = TestCasePhaseHelpForPhaseWithInstructions(
            'phase name',
            single_line_description('single line description'),
            non_empty_instruction_set('phase name'))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_description_with_rest_part(self):
        # ARRANGE
        tcp_help = TestCasePhaseHelpForPhaseWithInstructions(
            'phase name',
            Description('single line description',
                        [para('rest part para 1'),
                         para('rest part para 2')]),
            non_empty_instruction_set('phase name'))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)


def non_empty_instruction_set(phase_name: str) -> TestCasePhaseInstructionSet:
    return test_case_phase_instruction_set(phase_name,
                                           ['instr1'])


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRenderHelpSansInstructions),
        unittest.makeSuite(TestRenderHelpWithInstructions),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
