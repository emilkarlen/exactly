from shellcheck_lib.cli.instruction_setup import InstructionsSetup
from shellcheck_lib.cli.execution_mode.help import execution as help_execution
from shellcheck_lib.cli.execution_mode.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.test_case import execution as test_case_execution
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings
from shellcheck_lib.cli import main_program


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: main_program.StdOutputFiles,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup):
        super().__init__(output)
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self._instruction_setup = instruction_setup

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        executor = test_case_execution.Executor(self._std,
                                                self._split_line_into_name_and_argument_function,
                                                self._instruction_setup,
                                                settings)
        return executor.execute()

    def execute_help(self, settings: HelpSettings) -> int:
        help_execution.PrintInstructionsPerPhase(self._std).apply(self._instruction_setup)
        return 0
