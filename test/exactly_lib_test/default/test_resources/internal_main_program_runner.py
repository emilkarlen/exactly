import unittest

from exactly_lib.default.program_modes.test_case.default_instructions_setup import INSTRUCTIONS_SETUP
from exactly_lib.test_case.instruction_setup import InstructionsSetup
from exactly_lib_test.cli.test_resources.execute_main_program import execute_main_program
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult


class RunViaMainProgramInternally(MainProgramRunner):
    def __init__(self,
                 instructions_setup: InstructionsSetup = INSTRUCTIONS_SETUP):
        self.instructions_setup = instructions_setup

    def description_for_test_name(self) -> str:
        return 'run internally'

    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return execute_main_program(arguments,
                                    self.instructions_setup)
