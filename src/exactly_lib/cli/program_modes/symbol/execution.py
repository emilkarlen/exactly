from abc import ABC, abstractmethod
from typing import Tuple

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.program_modes.symbol.impl import symbol_usage_resolving
from exactly_lib.cli.program_modes.symbol.impl.parse_error_reporter import ParseErrorReporter
from exactly_lib.cli.program_modes.symbol.report import ReportGenerator
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest, RequestVariantVisitor, \
    RequestVariantList, RequestVariantIndividual
from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.common import result_reporting
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.actor import ParseException, ActionToCheck
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util import file_printer
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.std import StdOutputFiles


class _Parser(ABC):
    def __init__(self, completion_reporter: ParseErrorReporter):
        self.completion_reporter = completion_reporter

    @abstractmethod
    def parse(self) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        pass

    def _from_test_case(self,
                        test_case: test_case_doc.TestCase,
                        act_phase_setup: ActPhaseSetup) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:

        test_case_with_instructions = test_case.as_test_case_of_instructions()
        act_phase_instructions = [
            element.value
            for element in test_case_with_instructions.act_phase
        ]
        try:
            action_to_check = act_phase_setup.actor.parse(act_phase_instructions)
        except ParseException as ex:
            raise _ParseError(self.completion_reporter.report_act_phase_parse_error(ex))

        return (test_case_with_instructions,
                action_to_check)


def execute(request: SymbolInspectionRequest,
            test_case_definition: TestCaseDefinition,
            suite_configuration_section_parser: SectionElementParser,
            output: StdOutputFiles,
            ) -> int:
    def parser_for_request() -> _Parser:
        error_reporter = ParseErrorReporter(output)
        if request.is_inspect_test_case:
            return _ParserForTestCase(request.case_settings,
                                      test_case_definition,
                                      suite_configuration_section_parser,
                                      error_reporter)
        else:
            return _ParserForTestSuite(request.suite_settings,
                                       test_case_definition,
                                       suite_configuration_section_parser,
                                       error_reporter)

    parser = parser_for_request()
    try:
        test_case, action_to_check = parser.parse()
    except _ParseError as ex:
        return ex.exit_code

    definitions_resolver = symbol_usage_resolving.DefinitionsInfoResolverFromTestCase(
        test_case,
        action_to_check.symbol_usages()
    )
    report_generator = _RequestHandler().visit(request.variant)

    report = report_generator.generate(definitions_resolver)

    major_blocks_renderer = rend_comb.ConstantSequenceR([block.render() for block in report.blocks()])

    output_file, exit_code = (
        (output.out, exit_codes.EXIT_OK)
        if report.is_success
        else
        (output.err, exit_values.EXECUTION__HARD_ERROR.exit_code)
    )

    result_reporting.print_major_blocks(major_blocks_renderer,
                                        file_printer.file_printer_with_color_if_terminal(output_file))
    return exit_code


class _ParseError(Exception):
    def __init__(self, exit_code: int):
        self.exit_code = exit_code


class _ParserForTestSuite(_Parser):
    def __init__(self,
                 execution_settings: TestSuiteExecutionSettings,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 completion_reporter: ParseErrorReporter,
                 ):
        super().__init__(completion_reporter)
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.execution_settings = execution_settings

    def parse(self) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        from exactly_lib.test_suite.file_reading import suite_file_reading

        try:
            suite_doc = suite_file_reading.read_suite_document(self.execution_settings.suite_root_file_path,
                                                               self.suite_configuration_section_parser,
                                                               self.test_case_definition.parsing_setup)

        except SuiteParseError as ex:
            raise _ParseError(self.completion_reporter.report_suite_error(ex))

        conf_env = suite_file_reading.derive_conf_section_environment(suite_doc,
                                                                      self.execution_settings.handling_setup)

        return self._from_test_case(suite_doc.case_phases, conf_env.act_phase_setup)


class _ParserForTestCase(_Parser):
    def __init__(self,
                 execution_settings: TestCaseExecutionSettings,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 completion_reporter: ParseErrorReporter,
                 ):
        super().__init__(completion_reporter)
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.execution_settings = execution_settings

    def parse(self) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        try:
            accessor, act_phase_setup = self._accessor()
        except SuiteParseError as ex:
            raise _ParseError(self.completion_reporter.report_suite_error(ex))

        try:
            test_case = accessor.apply(self._test_case_file_ref())
        except AccessorError as ex:
            raise _ParseError(self.completion_reporter.report_access_error(ex))

        return self._from_test_case(test_case, act_phase_setup)

    def _accessor(self) -> Tuple[test_case_processing.Accessor, ActPhaseSetup]:
        case_execution_settings = self.execution_settings

        accessor_resolver = AccessorResolver(self.test_case_definition.parsing_setup,
                                             self.suite_configuration_section_parser,
                                             case_execution_settings.handling_setup)
        return accessor_resolver.resolve(case_execution_settings.test_case_file_path,
                                         case_execution_settings.run_as_part_of_explicit_suite)

    def _test_case_file_ref(self) -> test_case_processing.TestCaseFileReference:
        return test_case_processing.test_case_reference_of_source_file(
            self.execution_settings.test_case_file_path)


class _RequestHandler(RequestVariantVisitor[ReportGenerator]):
    def visit_list(self, list_variant: RequestVariantList) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.list_all import ListReportGenerator

        return ListReportGenerator()

    def visit_individual(self, individual_variant: RequestVariantIndividual) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.individual import IndividualReportGenerator

        return IndividualReportGenerator(individual_variant.name,
                                         individual_variant.list_references)
