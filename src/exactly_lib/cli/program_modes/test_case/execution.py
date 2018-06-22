import pathlib

from exactly_lib.cli.program_modes.test_case import result_reporting
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import parsing_configuration
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_suite.instruction_set.parse import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles


def execute(std_output_files: StdOutputFiles,
            test_case_definition: TestCaseDefinition,
            configuration_section_parser: parsing_configuration.SectionElementParser,
            settings: TestCaseExecutionSettings,
            act_phase_os_process_executor: ActPhaseOsProcessExecutor,
            ) -> int:
    result_reporter = _get_reporter(std_output_files, settings.reporting_option)
    try:
        handling_setup = _resolve_handling_setup(settings.handling_setup,
                                                 configuration_section_parser,
                                                 test_case_definition.parsing_setup,
                                                 settings.suite_to_read_config_from)
    except SuiteSyntaxError as ex:
        reporter = result_reporting.TestSuiteSyntaxErrorReporter(std_output_files)
        return reporter.report(ex)
    configuration = processors.Configuration(test_case_definition,
                                             handling_setup,
                                             act_phase_os_process_executor,
                                             result_reporter.depends_on_result_in_sandbox(),
                                             settings.sandbox_root_dir_resolver,
                                             result_reporter.execute_atc_and_skip_assertions())
    result = _process(settings.test_case_file_path,
                      configuration)
    return result_reporter.report(result)


def _process(test_case_file_path: pathlib.Path,
             configuration: processors.Configuration,
             ) -> test_case_processing.Result:
    processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
    return processor.apply(test_case_processing.test_case_setup_of_source_file(test_case_file_path))


def _get_reporter(std_output_files: StdOutputFiles,
                  reporting_option: ReportingOption) -> result_reporting.TestCaseResultReporter:
    return result_reporting.RESULT_REPORTERS[reporting_option](std_output_files)


def _resolve_handling_setup(default_handling_setup: TestCaseHandlingSetup,
                            configuration_section_parser: parsing_configuration.SectionElementParser,
                            test_case_parsing_setup: TestCaseParsingSetup,
                            suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    if not suite_to_read_config_from:
        return default_handling_setup
    from exactly_lib.test_suite.suite_file_reading import resolve_handling_setup_from_suite_file
    return resolve_handling_setup_from_suite_file(default_handling_setup,
                                                  configuration_section_parser,
                                                  test_case_parsing_setup,
                                                  suite_to_read_config_from)
