import types
import unittest

from exactly_lib.default.instruction_name_and_argument_splitter import \
    splitter as default_splitter
from exactly_lib.default.program_modes.test_case.default_instructions_setup import INSTRUCTIONS_SETUP
from exactly_lib.default.program_modes.test_case.execution_properties import PREDEFINED_PROPERTIES
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib_test.cli.test_resources.execute_main_program import execute_main_program, \
    first_char_is_name_and_rest_is_argument__splitter
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult


class RunViaMainProgramInternally(MainProgramRunner):
    def __init__(self,
                 instructions_setup: InstructionsSetup = INSTRUCTIONS_SETUP,
                 name_and_argument_splitter: types.FunctionType = first_char_is_name_and_rest_is_argument__splitter,
                 predefined_properties: PredefinedProperties = PredefinedProperties(),
                 ):
        self.instructions_setup = instructions_setup
        self.name_and_argument_splitter = name_and_argument_splitter
        self.predefined_properties = predefined_properties

    def description_for_test_name(self) -> str:
        return 'run internally'

    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return execute_main_program(arguments,
                                    self.instructions_setup,
                                    predefined_properties=self.predefined_properties,
                                    name_and_argument_splitter=self.name_and_argument_splitter)


def main_program_runner_with_default_setup__in_same_process() -> RunViaMainProgramInternally:
    return RunViaMainProgramInternally(instructions_setup=INSTRUCTIONS_SETUP,
                                       predefined_properties=PREDEFINED_PROPERTIES,
                                       name_and_argument_splitter=default_splitter)
