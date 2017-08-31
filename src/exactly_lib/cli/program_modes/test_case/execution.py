from exactly_lib.cli.program_modes.test_case.result_reporting import ResultReporter
from exactly_lib.cli.program_modes.test_case.settings import Output, TestCaseExecutionSettings
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.util.std import StdOutputFiles


class Executor:
    def __init__(self,
                 output: StdOutputFiles,
                 test_case_definition: TestCaseDefinition,
                 settings: TestCaseExecutionSettings):
        self._test_case_definition = test_case_definition
        self._settings = settings
        self._result_reporter = ResultReporter(output,
                                               settings.output)

    def execute(self) -> int:
        is_keep_sandbox = self._derive_should_keep_sandbox()
        result = self._process(is_keep_sandbox)
        return self._result_reporter.report(result)

    def _derive_should_keep_sandbox(self) -> bool:
        if self._settings.output is Output.ACT_PHASE_OUTPUT:
            return True
        else:
            return self._settings.is_keep_sandbox

    def _process(self,
                 is_keep_sds: bool) -> test_case_processing.Result:
        configuration = processors.Configuration(self._test_case_definition,
                                                 self._settings.handling_setup,
                                                 is_keep_sds,
                                                 self._settings.sandbox_directory_root_name_prefix)
        processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
        return processor.apply(test_case_processing.TestCaseSetup(self._settings.file_path))
