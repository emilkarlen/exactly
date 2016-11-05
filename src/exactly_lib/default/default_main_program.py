import datetime

from exactly_lib import program_info
from exactly_lib.cli import main_program
from exactly_lib.cli.program_modes.test_case import execution as test_case_execution
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite.reporting import RootSuiteReporterFactory
from exactly_lib.util.std import StdOutputFiles


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: StdOutputFiles,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 default: TestCaseHandlingSetup,
                 root_suite_reporter_factory: RootSuiteReporterFactory):
        super().__init__(output, instruction_setup, default)
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self.root_suite_reporter_factory = root_suite_reporter_factory

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        executor = test_case_execution.Executor(self._std,
                                                self._split_line_into_name_and_argument_function,
                                                self._instruction_set,
                                                settings)
        return executor.execute()

    def execute_test_suite(self, test_suite_execution_settings) -> int:
        from exactly_lib.processing import processors as case_processing
        from exactly_lib.test_suite import execution as test_suite_execution
        from exactly_lib.test_suite import enumeration
        from exactly_lib.test_suite import suite_hierarchy_reading
        default_configuration = case_processing.Configuration(self._split_line_into_name_and_argument_function,
                                                              self._instruction_set,
                                                              test_suite_execution_settings.handling_setup,
                                                              False,
                                                              self._eds_root_name_prefix_for_suite())
        executor = test_suite_execution.Executor(default_configuration,
                                                 self._output,
                                                 suite_hierarchy_reading.Reader(
                                                     suite_hierarchy_reading.Environment(
                                                         default_configuration.default_handling_setup.preprocessor,
                                                         default_configuration.default_handling_setup.default_act_phase_setup)),
                                                 self.root_suite_reporter_factory,
                                                 enumeration.DepthFirstEnumerator(),
                                                 case_processing.new_processor_that_should_not_pollute_current_process,
                                                 test_suite_execution_settings.suite_root_file_path)
        return executor.execute()

    @staticmethod
    def _eds_root_name_prefix_for_suite():
        today = datetime.datetime.today()
        datetime_suffix = today.strftime('%Y-%m-%d-%H-%M-%S')
        execution_directory_root_name_prefix = program_info.PROGRAM_NAME + '-suite-' + datetime_suffix + '-'
        return execution_directory_root_name_prefix
