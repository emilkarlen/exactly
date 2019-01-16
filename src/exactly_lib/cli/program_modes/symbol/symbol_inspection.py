from typing import Tuple

from exactly_lib.cli.program_modes.symbol.completion_reporter import CompletionReporter
from exactly_lib.cli.program_modes.symbol.report_generator import ReportGenerator
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case.act_phase_handling import ParseException
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles


class SymbolInspectionRequest:
    def __init__(self,
                 case_execution_settings: TestCaseExecutionSettings):
        self.case_execution_settings = case_execution_settings


class Executor:
    def __init__(self,
                 request: SymbolInspectionRequest,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 output: StdOutputFiles,
                 ):
        self.output = output
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.request = request
        self.completion_reporter = CompletionReporter(output)

    def execute(self) -> int:
        try:
            accessor, act_phase_setup = self._accessor()
        except SuiteSyntaxError as ex:
            return self.completion_reporter.report_suite_error(ex)

        try:
            test_case_with_section_elements = accessor.apply(self._test_case_file_ref())
        except AccessorError as ex:
            return self.completion_reporter.report_access_error(ex)

        test_case = test_case_with_section_elements.as_test_case_of_instructions()

        try:
            atc_executor = act_phase_setup.atc_executor_parser.parse(test_case.act_phase)
        except ParseException as ex:
            return self.completion_reporter.report_act_phase_parse_error(ex)

        report_generator = ReportGenerator(
            self.output,
            self.completion_reporter,
            test_case,
            atc_executor.symbol_usages())

        return report_generator.list()

    def _accessor(self) -> Tuple[test_case_processing.Accessor, ActPhaseSetup]:
        case_execution_settings = self.request.case_execution_settings

        accessor_resolver = AccessorResolver(self.test_case_definition.parsing_setup,
                                             self.suite_configuration_section_parser,
                                             case_execution_settings.handling_setup)
        return accessor_resolver.resolve(case_execution_settings.test_case_file_path,
                                         case_execution_settings.run_as_part_of_explicit_suite)

    def _test_case_file_ref(self) -> test_case_processing.TestCaseFileReference:
        return test_case_processing.test_case_reference_of_source_file(
            self.request.case_execution_settings.test_case_file_path)
