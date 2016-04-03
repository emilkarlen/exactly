import unittest

from shellcheck_lib.help.program_modes.test_case.contents.phase import act
from shellcheck_lib.help.program_modes.test_case.contents.phase import \
    assert_, configuration, before_assert, cleanup, setup
from shellcheck_lib.help.program_modes.test_case.render import test_case_phase as sut
from shellcheck_lib_test.help.test_resources import test_case_phase_instruction_set
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


class TestCase(unittest.TestCase):
    def test_configuration(self):
        # ARRANGE #
        tcp_help = configuration.ConfigurationPhaseDocumentation(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseOverviewRenderer(tcp_help).apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_setup(self):
        # ARRANGE #
        tcp_help = setup.SetupPhaseDocumentation(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseOverviewRenderer(tcp_help).apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_act(self):
        # ARRANGE #
        tcp_help = act.ActPhaseDocumentation('phase name')
        # ACT #
        actual = sut.TestCasePhaseOverviewRenderer(tcp_help).apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_before_assert(self):
        # ARRANGE #
        tcp_help = before_assert.BeforeAssertPhaseDocumentation(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseOverviewRenderer(tcp_help).apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_assert(self):
        # ARRANGE #
        tcp_help = assert_.AssertPhaseDocumentation(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseOverviewRenderer(tcp_help).apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_cleanup(self):
        # ARRANGE
        tcp_help = cleanup.CleanupPhaseDocumentation(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT #
        actual = sut.TestCasePhaseOverviewRenderer(tcp_help).apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
