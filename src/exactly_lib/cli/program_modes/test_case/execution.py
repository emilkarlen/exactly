from exactly_lib.cli.program_modes.test_case import result_reporting
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.util.std import StdOutputFiles


class Executor:
    def __init__(self,
                 std_output_files: StdOutputFiles,
                 test_case_definition: TestCaseDefinition,
                 settings: TestCaseExecutionSettings):
        self._test_case_definition = test_case_definition
        self._settings = settings
        self._result_reporter = get_reporter(std_output_files,
                                             settings)

    def execute(self) -> int:
        is_keep_sandbox = self._result_reporter.depends_on_result_in_sandbox()
        result = self._process(is_keep_sandbox)
        return self._result_reporter.report(result)

    def _process(self,
                 is_keep_sds: bool) -> test_case_processing.Result:
        configuration = processors.Configuration(self._test_case_definition,
                                                 self._settings.handling_setup,
                                                 is_keep_sds,
                                                 self._settings.sandbox_directory_root_name_prefix)
        processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
        return processor.apply(test_case_processing.TestCaseSetup(self._settings.file_path))


def get_reporter(std_output_files: StdOutputFiles,
                 settings: TestCaseExecutionSettings) -> result_reporting.ResultReporter:
    return result_reporting.RESULT_REPORTERS[settings.reporting_option](std_output_files)
