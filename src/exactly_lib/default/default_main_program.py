import datetime

from exactly_lib import program_info
from exactly_lib.cli import main_program
from exactly_lib.cli.program_modes.test_case import execution as test_case_execution
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util.std import StdOutputFiles


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: StdOutputFiles,
                 test_case_definition: TestCaseDefinition,
                 default: TestCaseHandlingSetup):
        super().__init__(output, test_case_definition.instruction_setup, default)
        self._test_case_definition = test_case_definition

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        return test_case_execution.execute(self._std,
                                           self._test_case_definition,
                                           settings)

    def execute_test_suite(self, test_suite_execution_settings) -> int:
        from exactly_lib.processing import processors
        from exactly_lib.test_suite import enumeration
        from exactly_lib.test_suite import suite_hierarchy_reading
        from exactly_lib.test_suite import execution as test_suite_execution
        default_configuration = processors.Configuration(self._test_case_definition,
                                                         test_suite_execution_settings.handling_setup,
                                                         False,
                                                         self._sds_root_name_prefix_for_suite())
        executor = test_suite_execution.Executor(default_configuration,
                                                 self._output,
                                                 suite_hierarchy_reading.Reader(
                                                     suite_hierarchy_reading.Environment(
                                                         default_configuration.default_handling_setup.preprocessor,
                                                         default_configuration.default_handling_setup.default_act_phase_setup)
                                                 ),
                                                 test_suite_execution_settings.reporter_factory,
                                                 enumeration.DepthFirstEnumerator(),
                                                 processors.new_processor_that_should_not_pollute_current_process,
                                                 test_suite_execution_settings.suite_root_file_path)
        return executor.execute()

    @staticmethod
    def _sds_root_name_prefix_for_suite():
        today = datetime.datetime.today()
        datetime_suffix = today.strftime('%Y-%m-%d-%H-%M-%S')
        sandbox_directory_root_name_prefix = program_info.PROGRAM_NAME + '-suite-' + datetime_suffix + '-'
        return sandbox_directory_root_name_prefix
