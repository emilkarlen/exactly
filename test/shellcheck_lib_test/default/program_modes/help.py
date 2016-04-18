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
from shellcheck_lib_test.test_resources import process_result_assertions as pr
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase, Arrangement
from shellcheck_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.value_assertion_str import is_empty


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHelp)


def suite_for_main_program(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite_for_test_cases(main_program_test_cases(), main_program_runner)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


def main_program_test_cases() -> list:
    return [
        ProcessTestCase('WHEN command line arguments are invalid THEN'
                        ' exit code SHOULD indicate this'
                        ' AND stdout SHOULD be empty',
                        HelpInvokationArrangement(['too', 'many', 'arguments', ',', 'indeed']),
                        va.And([
                            pr.is_result_for_exit_code(main_program.EXIT_INVALID_USAGE),
                            pr.stdout(is_empty())
                        ])),
    ]


class HelpInvokationArrangement(Arrangement):
    def __init__(self,
                 help_arguments: list):
        self.help_arguments = help_arguments

    def command_line_arguments(self) -> list:
        return [main_program.HELP_COMMAND] + self.help_arguments


class TestHelp(unittest.TestCase):
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
