import types
import unittest

from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.cli.test_resources import execute_main_program
from exactly_lib_test.cli.test_resources.main_program_runner_utils import \
    first_char_is_name_and_rest_is_argument__splitter, EMPTY_INSTRUCTIONS_SETUP
from exactly_lib_test.cli.test_resources.test_case_handling_setup import test_case_handling_setup
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult


class RunViaMainProgramInternally(MainProgramRunner):
    def __init__(self,
                 the_test_case_handling_setup: TestCaseHandlingSetup = test_case_handling_setup(),
                 instructions_setup: InstructionsSetup = EMPTY_INSTRUCTIONS_SETUP,
                 test_suite_definition: TestSuiteDefinition = execute_main_program.test_suite_definition(),
                 name_and_argument_splitter: types.FunctionType = first_char_is_name_and_rest_is_argument__splitter,
                 builtin_symbols: list = (),
                 ):
        self.test_suite_definition = test_suite_definition
        self.instructions_setup = instructions_setup
        self.name_and_argument_splitter = name_and_argument_splitter
        self.builtin_symbols = list(builtin_symbols)
        self.the_test_case_handling_setup = the_test_case_handling_setup

    def description_for_test_name(self) -> str:
        return 'run internally'

    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return execute_main_program.execute_main_program(arguments,
                                                         self.the_test_case_handling_setup,
                                                         self.instructions_setup,
                                                         builtin_symbols=self.builtin_symbols,
                                                         name_and_argument_splitter=self.name_and_argument_splitter,
                                                         test_suite_definition=self.test_suite_definition)
