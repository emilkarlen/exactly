from typing import Tuple

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.program_modes.symbol.impl import symbol_usage_resolving
from exactly_lib.cli.program_modes.symbol.impl.parse import Parser, ParserForTestSuite, ParserForTestCase
from exactly_lib.cli.program_modes.symbol.impl.report import ReportGenerator, Report
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest, RequestVariantVisitor, \
    RequestVariantList, RequestVariantIndividual
from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment, StdOutputFilePrinters
from exactly_lib.common.process_result_reporters import ProcessResultReporterOfMajorBlocksBase
from exactly_lib.processing import exit_values
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import result_reporting as processing_result_reporting
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import actor
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.actor import ActionToCheck
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.std import StdOutputFiles


class Executor:
    def __init__(self,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 ):
        self._suite_configuration_section_parser = suite_configuration_section_parser
        self._test_case_definition = test_case_definition

    def execution_reporter(self, request: SymbolInspectionRequest) -> ProcessResultReporter:
        try:
            test_case, action_to_check = self._parse(request)
        except SuiteParseError as ex:
            return _SuiteErrorReporter(ex)
        except AccessorError as ex:
            return _AccessErrorReporter(ex)
        except actor.ParseException:
            return _ActPhaseErrorReporter()

        return _ReporterOfRequestReport(
            self._generate_report(test_case, action_to_check, request)
        )

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


class _RequestHandler(RequestVariantVisitor[ReportGenerator]):
    def visit_list(self, list_variant: RequestVariantList) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.list_all import ListReportGenerator

        return ListReportGenerator()

    def visit_individual(self, individual_variant: RequestVariantIndividual) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.individual import IndividualReportGenerator

        return IndividualReportGenerator(individual_variant.name,
                                         individual_variant.list_references)


class _SuiteErrorReporter(ProcessResultReporter):
    def __init__(self, ex: SuiteParseError):
        self._ex = ex

    def report(self, environment: Environment) -> int:
        output_files = environment.std_files
        output_printers = environment.std_file_printers
        err_only_output = Environment(
            StdOutputFiles(output_files.err, output_files.err),
            StdOutputFilePrinters(output_printers.err, output_printers.err)
        )

        reporter = processing_result_reporting.TestSuiteParseErrorReporter(err_only_output)

        return reporter.report(self._ex)


class _AccessErrorReporter(ProcessResultReporter):
    def __init__(self, ex: AccessorError):
        self._ex = ex

    def report(self, environment: Environment) -> int:
        exit_value = exit_values.from_access_error(self._ex.error)
        environment.err_printer.write_colored_line(exit_value.exit_identifier,
                                                   exit_value.color)
        return exit_value.exit_code


class _ActPhaseErrorReporter(ProcessResultReporter):
    def report(self, environment: Environment) -> int:
        exit_value = exit_values.EXECUTION__VALIDATION_ERROR
        environment.err_printer.write_colored_line(exit_value.exit_identifier,
                                                   exit_value.color)
        return exit_value.exit_code


class _ReporterOfRequestReport(ProcessResultReporterOfMajorBlocksBase):
    def __init__(self, report: Report):
        output_file, exit_code = (
            (ProcOutputFile.STDOUT, exit_codes.EXIT_OK)
            if report.is_success
            else
            (ProcOutputFile.STDERR, exit_values.EXECUTION__HARD_ERROR.exit_code)
        )
        super().__init__(exit_code, output_file)
        self._report = report

    def _blocks(self) -> SequenceRenderer[MajorBlock]:
        return rend_comb.ConstantSequenceR([
            block.render()
            for block in self._report.blocks()
        ])
