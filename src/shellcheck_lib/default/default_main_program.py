from shellcheck_lib.cli.execution_mode.test_suite.settings import Settings
from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.cli.execution_mode.help import execution as help_execution
from shellcheck_lib.cli.execution_mode.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.test_case import execution as test_case_execution
from shellcheck_lib.test_suite import execution as test_suite_execution
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings
from shellcheck_lib.cli import main_program
from shellcheck_lib.general.output import StdOutputFiles


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: StdOutputFiles,
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

    def execute_test_suite(self, settings: Settings) -> int:
        executor = test_suite_execution.Executor(self._output,
                                                 settings)
        return executor.execute()

    def execute_help(self, settings: HelpSettings) -> int:
        help_execution.PrintInstructionsPerPhase(self._std).apply(self._instruction_setup)
        return 0
