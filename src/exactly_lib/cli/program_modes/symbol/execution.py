from typing import Tuple, Optional

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.program_modes.symbol.impl import symbol_usage_resolving
from exactly_lib.cli.program_modes.symbol.impl.report import ReportGenerator, Report
from exactly_lib.cli.program_modes.symbol.impl.resolve import Resolver, ResolverForTestSuite, ResolverForTestCase
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest, RequestVariantVisitor, \
    RequestVariantList, RequestVariantIndividual
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment, StdOutputFilePrinters
from exactly_lib.common.process_result_reporters import ProcessResultReporterOfMajorBlocksBase, \
    ProcessResultReporterOfExitCodeAndMajorBlocksBase
from exactly_lib.common.report_rendering.parts import failure_info as failure_info_rendering
from exactly_lib.execution.full_execution import result
from exactly_lib.execution.result import PhaseStepFailureException, PhaseStepFailure
from exactly_lib.processing import exit_values
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import result_reporting
from exactly_lib.processing.standalone import result_reporting as processing_result_reporting
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import actor
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.actor import ActionToCheck
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util import symbol_table
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable


class Executor:
    def __init__(self,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 ):
        self._suite_configuration_section_parser = suite_configuration_section_parser
        self._test_case_definition = test_case_definition

    def execution_reporter(self, request: SymbolInspectionRequest) -> ProcessResultReporter:
        try:
            test_case, action_to_check = self._resolve(request)
        except SuiteParseError as ex:
            return _SuiteErrorReporter(ex)
        except AccessorError as ex:
            return _reporter_of_access_error(ex)
        except actor.ParseException as ex:
            return _ActPhaseErrorReporter(ex)
        except PhaseStepFailureException as ex:
            return _PhaseStepErrorReporter(ex.failure)

        report_generator = self._report_generator(request)
        return _ReporterOfRequestReport(
            self._generate_report(test_case, action_to_check, report_generator)
        )

    def _resolve(self, request: SymbolInspectionRequest) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        return self._resolver_for_request(request).resolve()

    def _resolver_for_request(self, request: SymbolInspectionRequest) -> Resolver:
        if request.is_inspect_test_case:
            return ResolverForTestCase(request.case_settings,
                                       self._test_case_definition,
                                       self._suite_configuration_section_parser)
        else:
            return ResolverForTestSuite(request.suite_settings,
                                        self._test_case_definition,
                                        self._suite_configuration_section_parser)

    def _report_generator(self, request: SymbolInspectionRequest) -> ReportGenerator:
        request_handler = _RequestHandler(self._test_case_definition.predefined_properties.predefined_symbols)
        return request_handler.visit(request.variant)

    def _generate_report(self, test_case: test_case_doc.TestCaseOfInstructions,
                         action_to_check: ActionToCheck,
                         report_generator: ReportGenerator,
                         ) -> Report:
        definitions_resolver = symbol_usage_resolving.DefinitionsInfoResolverFromTestCase(
            test_case,
            action_to_check.symbol_usages(),
            self._test_case_definition.predefined_properties.predefined_symbols,
        )

        return report_generator.generate(definitions_resolver)


class _RequestHandler(RequestVariantVisitor[ReportGenerator]):
    def __init__(self, builtin_symbols: Optional[SymbolTable]):
        self._builtin_symbols = symbol_table.symbol_table_from_none_or_value(builtin_symbols)

    def visit_list(self, list_variant: RequestVariantList) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.list_all import ListReportGenerator

        return ListReportGenerator()

    def visit_individual(self, individual_variant: RequestVariantIndividual) -> ReportGenerator:
        from exactly_lib.cli.program_modes.symbol.impl.reports.individual import IndividualReportGenerator

        return IndividualReportGenerator(individual_variant.name,
                                         individual_variant.list_references,
                                         self._builtin_symbols)


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


def _reporter_of_access_error(ex: AccessorError) -> ProcessResultReporter:
    return result_reporting.reporter_of_unable_to_execute(
        ProcOutputFile.STDERR,
        exit_values.from_access_error(ex.error),
        ex.error_info,
    )


class _ActPhaseErrorReporter(ProcessResultReporterOfExitCodeAndMajorBlocksBase):
    def __init__(self, ex: actor.ParseException):
        super().__init__(ProcOutputFile.STDERR,
                         ProcOutputFile.STDERR)
        self._ex = ex

    def _exit_value(self) -> ExitValue:
        return exit_values.EXECUTION__VALIDATION_ERROR

    def _blocks(self) -> SequenceRenderer[MajorBlock]:
        return self._ex.cause.failure_message


class _PhaseStepErrorReporter(ProcessResultReporterOfExitCodeAndMajorBlocksBase):
    def __init__(self, failure: PhaseStepFailure):
        super().__init__(ProcOutputFile.STDERR,
                         ProcOutputFile.STDERR)
        self._failure = failure

    def _exit_value(self) -> ExitValue:
        return exit_values.from_full_result(
            result.translate_status(TestCaseStatus.PASS,
                                    self._failure.status)
        )

    def _blocks(self) -> SequenceRenderer[MajorBlock]:
        return failure_info_rendering.FailureInfoRenderer(self._failure.failure_info)


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
