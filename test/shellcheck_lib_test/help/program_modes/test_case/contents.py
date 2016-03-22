import unittest

from shellcheck_lib.help.program_modes.test_case.contents.phase import act
from shellcheck_lib.help.program_modes.test_case.contents.phase import \
    assert_, configuration, before_assert, cleanup, setup
from shellcheck_lib.help.program_modes.test_case.render import test_case_phase as sut
from shellcheck_lib_test.help.test_resources import test_case_phase_instruction_set
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


class TestCase(unittest.TestCase):
    def test_configuration(self):
        # ARRANGE
        tcp_help = configuration.ConfigurationPhaseHelp(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_setup(self):
        # ARRANGE
        tcp_help = setup.SetupPhaseHelp(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_act(self):
        # ARRANGE
        tcp_help = act.ActPhaseHelp('phase name')
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_before_assert(self):
        # ARRANGE
        tcp_help = before_assert.BeforeAssertPhaseHelp(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_assert(self):
        # ARRANGE
        tcp_help = assert_.AssertPhaseHelp(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)

    def test_cleanup(self):
        # ARRANGE
        tcp_help = cleanup.CleanupPhaseHelp(
            'phase name',
            test_case_phase_instruction_set('phase name',
                                            ['instr 1',
                                             'instr 2']))
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        # ASSERT
        struct_check.is_section_contents.apply(self, actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
