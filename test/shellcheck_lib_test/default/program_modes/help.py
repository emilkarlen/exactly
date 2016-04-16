import unittest

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.main_program import HELP_COMMAND
from shellcheck_lib.cli.program_modes.help import arguments_for
from shellcheck_lib.default.program_modes.test_case.default_instructions_setup import INSTRUCTIONS_SETUP
from shellcheck_lib.execution import phases
from shellcheck_lib.help.concepts.concept import SANDBOX_CONCEPT
from shellcheck_lib.help.program_modes.test_case.config import phase_help_name
from shellcheck_lib.test_suite.parser import SECTION_NAME__SUITS, SECTION_NAME__CASES
from shellcheck_lib_test.cli.test_resources.execute_main_program import execute_main_program


class TestHelp(unittest.TestCase):
    def test_invalid_usage(self):
        # ARRANGE #
        command_line_arguments = self._cl(['too', 'many', 'arguments', ',', 'indeed'])
        sub_process_result = execute_main_program(command_line_arguments)
        # ASSERT #
        self.assertEqual(main_program.EXIT_INVALID_USAGE,
                         sub_process_result.exitcode,
                         'Exit Status')
        self.assertEqual('',
                         sub_process_result.stdout,
                         'Output on stdout')
        self.assertTrue(len(sub_process_result.stderr) > 0)

    def test_program(self):
        self._assert_is_successful_invokation(arguments_for.program())

    def test_help(self):
        self._assert_is_successful_invokation(arguments_for.help_help())

    def test_html_doc(self):
        self._assert_is_successful_invokation(arguments_for.html_doc())

    def test_concept_list(self):
        self._assert_is_successful_invokation(arguments_for.concept_list())

    def test_individual_concept(self):
        self._assert_is_successful_invokation(arguments_for.individual_concept(SANDBOX_CONCEPT.name().singular))

    def test_case_phases(self):
        for ph in phases.ALL:
            self._assert_is_successful_invokation(arguments_for.phase(ph),
                                                  msg_header='Phase %s: ' + ph.identifier)

    def test_instructions(self):
        self._assert_is_successful_invokation(arguments_for.instructions())

    def test_instruction_search(self):
        self._assert_is_successful_invokation(arguments_for.instruction_search('home'))

    def test_instruction_in_phase(self):
        self._assert_is_successful_invokation(arguments_for.instruction_in_phase(phase_help_name(phases.ANONYMOUS),
                                                                                 'home'))

    def test_suite(self):
        self._assert_is_successful_invokation(arguments_for.suite())

    def test_suite_section__suites(self):
        self._assert_is_successful_invokation(arguments_for.suite_section(SECTION_NAME__SUITS))

    def test_suite_section__cases(self):
        self._assert_is_successful_invokation(arguments_for.suite_section(SECTION_NAME__CASES))

    def _assert_is_successful_invokation(self, help_command_arguments: list,
                                         msg_header: str = ''):
        command_line_arguments = self._cl(help_command_arguments)
        sub_process_result = execute_main_program(command_line_arguments,
                                                  instructions_setup=INSTRUCTIONS_SETUP)
        self.assertEqual(0,
                         sub_process_result.exitcode,
                         msg_header + 'Exit Status')

    @staticmethod
    def _cl(help_command_arguments: list) -> list:
        return [HELP_COMMAND] + help_command_arguments


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHelp)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
