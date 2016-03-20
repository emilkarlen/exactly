import unittest

from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseReference, TestCasePhaseHelp
from shellcheck_lib.help.program_modes.test_case.render import test_case_phase as sut
from shellcheck_lib.help.utils.description import single_line_description
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


class TestRender(unittest.TestCase):
    def test_without_instruction_set(self):
        # ARRANGE
        phase_ref = TestCasePhaseReference(single_line_description('single line'))
        tcp_help = TestCasePhaseHelp('phase name',
                                     phase_ref,
                                     None)
        # ACT
        actual = sut.render_test_case_phase_overview(tcp_help)
        struct_check.is_section_contents.apply(self, actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRender)
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
