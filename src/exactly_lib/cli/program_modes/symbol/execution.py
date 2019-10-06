from typing import Tuple

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.program_modes.symbol.impl import symbol_usage_resolving
from exactly_lib.cli.program_modes.symbol.impl.parse import Parser, ParserForTestSuite, ParserForTestCase
from exactly_lib.cli.program_modes.symbol.impl.report import ReportGenerator, Report
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest, RequestVariantVisitor, \
    RequestVariantList, RequestVariantIndividual
from exactly_lib.common import result_reporting
from exactly_lib.processing import exit_values
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import result_reporting as processing_result_reporting
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import actor
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.actor import ActionToCheck, ParseException
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util import file_printer
from exactly_lib.util.file_printer import file_printer_with_color_if_terminal
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.std import StdOutputFiles


class Executor:
    def __init__(self,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 ):
        self._suite_configuration_section_parser = suite_configuration_section_parser
        self._test_case_definition = test_case_definition

    def execute(self, request: SymbolInspectionRequest, output: StdOutputFiles) -> int:
        parse_error_reporter = _ParseErrorReporter(output)

        try:
            test_case, action_to_check = self._parse(request)
        except SuiteParseError as ex:
            return parse_error_reporter.report_suite_error(ex)
        except AccessorError as ex:
            return parse_error_reporter.report_access_error(ex)
        except actor.ParseException as ex:
            return parse_error_reporter.report_act_phase_parse_error(ex)

        report = self._generate_report(test_case, action_to_check, request)

        output_file, exit_code = (
            (output.out, exit_codes.EXIT_OK)
            if report.is_success
            else
            (output.err, exit_values.EXECUTION__HARD_ERROR.exit_code)
        )

        self._print_report(report, output_file)

        return exit_code

    def _parse(self, request: SymbolInspectionRequest) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        return self._parser_for_request(request).parse()

    def _parser_for_request(self, request: SymbolInspectionRequest) -> Parser:
        if request.is_inspect_test_case:
            return ParserForTestCase(request.case_settings,
                                     self._test_case_definition,
                                     self._suite_configuration_section_parser)
        else:
            return ParserForTestSuite(request.suite_settings,
                                      self._test_case_definition,
                                      self._suite_configuration_section_parser)

    @staticmethod
    def _generate_report(test_case: test_case_doc.TestCaseOfInstructions,
                         action_to_check: ActionToCheck,
                         request: SymbolInspectionRequest,
                         ) -> Report:
        definitions_resolver = symbol_usage_resolving.DefinitionsInfoResolverFromTestCase(
            test_case,
            action_to_check.symbol_usages()
        )
        report_generator = _RequestHandler().visit(request.variant)

        return report_generator.generate(definitions_resolver)

    @staticmethod
    def _print_report(report: Report, output_file):
        major_blocks_renderer = rend_comb.ConstantSequenceR([block.render() for block in report.blocks()])

        result_reporting.print_major_blocks(major_blocks_renderer,
                                            file_printer.file_printer_with_color_if_terminal(output_file))


class _RequestHandler(RequestVariantVisitor[ReportGenerator]):
    def visit_list(self, list_variant: RequestVariantList) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.list_all import ListReportGenerator

        return ListReportGenerator()

    def visit_individual(self, individual_variant: RequestVariantIndividual) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.individual import IndividualReportGenerator

        return IndividualReportGenerator(individual_variant.name,
                                         individual_variant.list_references)


class _ParseErrorReporter:
    def __init__(self, output: StdOutputFiles):
        self.output = output
        self.out_printer = file_printer_with_color_if_terminal(output.out)
        self.err_printer = file_printer_with_color_if_terminal(output.err)

    def report_suite_error(self, ex: SuiteParseError) -> int:
        err_only_output = StdOutputFiles(self.output.err,
                                         self.output.err)
        reporter = processing_result_reporting.TestSuiteParseErrorReporter(err_only_output)
        return reporter.report(ex)

    def report_access_error(self, error: AccessorError) -> int:
        exit_value = exit_values.from_access_error(error.error)
        self.err_printer.write_colored_line(exit_value.exit_identifier,
                                            exit_value.color)
        return exit_value.exit_code

    def report_act_phase_parse_error(self, error: ParseException) -> int:
        exit_value = exit_values.EXECUTION__VALIDATION_ERROR
        self.err_printer.write_colored_line(exit_value.exit_identifier,
                                            exit_value.color)
        return exit_value.exit_code
