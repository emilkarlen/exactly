from exactly_lib.cli.program_modes.test_case import result_reporting
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.test_suite.instruction_set.test_suite_definition import TestSuiteDefinition
from exactly_lib.util.std import StdOutputFiles


def execute(std_output_files: StdOutputFiles,
            test_case_definition: TestCaseDefinition,
            test_suite_definition: TestSuiteDefinition,
            settings: TestCaseExecutionSettings) -> int:
    result_reporter = _get_reporter(std_output_files,
                                    settings.reporting_option)
    is_keep_sandbox = result_reporter.depends_on_result_in_sandbox()
    result = _process(is_keep_sandbox,
                      test_case_definition,
                      settings)
    return result_reporter.report(result)


def _process(is_keep_sds: bool,
             test_case_definition: TestCaseDefinition,
             settings: TestCaseExecutionSettings
             ) -> test_case_processing.Result:
    configuration = processors.Configuration(test_case_definition,
                                             settings.handling_setup,
                                             is_keep_sds,
                                             settings.sandbox_directory_root_name_prefix)
    processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
    return processor.apply(test_case_processing.TestCaseSetup(settings.test_case_file_path))


def _get_reporter(std_output_files: StdOutputFiles,
                  reporting_option: ReportingOption) -> result_reporting.ResultReporter:
    return result_reporting.RESULT_REPORTERS[reporting_option](std_output_files)
