import pathlib

from exactly_lib.cli.program_modes.test_case import result_reporting
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import document_parser
from exactly_lib.test_suite import suite_file_reading
from exactly_lib.test_suite.instruction_set.parse import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles


def execute(std_output_files: StdOutputFiles,
            test_case_definition: TestCaseDefinition,
            configuration_section_parser: document_parser.SectionElementParser,
            settings: TestCaseExecutionSettings) -> int:
    result_reporter = _get_reporter(std_output_files,
                                    settings.reporting_option)
    is_keep_sandbox = result_reporter.depends_on_result_in_sandbox()

    try:
        handling_setup = _resolve_handling_setup(settings.handling_setup,
                                                 configuration_section_parser,
                                                 settings.suite_to_read_config_from)
    except SuiteSyntaxError as ex:
        reporter = result_reporting.TestSuiteSyntaxErrorReporter(std_output_files)
        return reporter.report(ex)
    result = _process(settings.test_case_file_path,
                      is_keep_sandbox,
                      test_case_definition,
                      handling_setup,
                      settings.sandbox_directory_root_name_prefix)
    return result_reporter.report(result)


def _process(test_case_file_path: pathlib.Path,
             is_keep_sds: bool,
             test_case_definition: TestCaseDefinition,
             handling_setup: TestCaseHandlingSetup,
             sandbox_directory_root_name_prefix: str,
             ) -> test_case_processing.Result:
    configuration = processors.Configuration(test_case_definition,
                                             handling_setup,
                                             is_keep_sds,
                                             sandbox_directory_root_name_prefix)
    processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
    return processor.apply(test_case_processing.TestCaseSetup(test_case_file_path))


def _get_reporter(std_output_files: StdOutputFiles,
                  reporting_option: ReportingOption) -> result_reporting.TestCaseResultReporter:
    return result_reporting.RESULT_REPORTERS[reporting_option](std_output_files)


def _resolve_handling_setup(default_handling_setup: TestCaseHandlingSetup,
                            configuration_section_parser: document_parser.SectionElementParser,
                            suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    if not suite_to_read_config_from:
        return default_handling_setup
    from exactly_lib.cli.program_modes.test_case.read_conf_from_suite import resolve_handling_setup_from_suite
    return resolve_handling_setup_from_suite(default_handling_setup,
                                             configuration_section_parser,
                                             suite_to_read_config_from)


def _resolve_handling_setup_from_suite(default_handling_setup: TestCaseHandlingSetup,
                                       configuration_section_parser: document_parser.SectionElementParser,
                                       suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    if not suite_to_read_config_from:
        return default_handling_setup

    suite_document = suite_file_reading.read_suite_document(suite_to_read_config_from,
                                                            configuration_section_parser)
    return suite_file_reading.resolve_test_case_handling_setup(suite_document,
                                                               default_handling_setup)
