import datetime

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.program_modes.test_case import execution as test_case_execution
from shellcheck_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.program_modes.test_suite.settings import Settings
from shellcheck_lib.default.execution_mode.test_case import processing as case_processing
from shellcheck_lib.default.execution_mode.test_suite import reporting as suite_reporting
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.test_case.preprocessor import IdentityPreprocessor
from shellcheck_lib.test_suite import enumeration
from shellcheck_lib.test_suite import execution as test_suite_execution
from shellcheck_lib.test_suite import suite_hierarchy_reading
from shellcheck_lib.util.std import StdOutputFiles


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: StdOutputFiles,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup):
        super().__init__(output, instruction_setup)
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        executor = test_case_execution.Executor(self._std,
                                                self._split_line_into_name_and_argument_function,
                                                self._instruction_set,
                                                settings)
        return executor.execute()

    def execute_test_suite(self, settings: Settings) -> int:
        default_configuration = case_processing.Configuration(self._split_line_into_name_and_argument_function,
                                                              self._instruction_set,
                                                              settings.act_phase_setup,
                                                              IdentityPreprocessor(),
                                                              False,
                                                              self._eds_root_name_prefix_for_suite())
        executor = test_suite_execution.Executor(default_configuration,
                                                 self._output,
                                                 suite_hierarchy_reading.Reader(
                                                         suite_hierarchy_reading.Environment(
                                                                 default_configuration.preprocessor)),
                                                 suite_reporting.ReporterFactory(),
                                                 enumeration.DepthFirstEnumerator(),
                                                 case_processing.new_processor_that_should_not_pollute_current_process,
                                                 settings.suite_root_file_path)
        return executor.execute()

    @staticmethod
    def _eds_root_name_prefix_for_suite():
        today = datetime.datetime.today()
        datetime_suffix = today.strftime('%Y-%m-%d-%H-%M-%S')
        execution_directory_root_name_prefix = 'shellcheck-suite-' + datetime_suffix + '-'
        return execution_directory_root_name_prefix
